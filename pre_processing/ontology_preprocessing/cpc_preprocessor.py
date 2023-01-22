import re
from io import StringIO
from typing import List

import numpy as np
import pandas as pd
from owlready2 import get_ontology

from ontology_preprocessing.clazz import Clazz
from ontology_preprocessing.owl_generator import generate_owl


class CPCPreprocessor:

    @staticmethod
    def preprocess_cpc_full(
            ontology_file_name_to_read: str,
            preprocessed_file_to_write: str,
            path_to_owl_template: str = None
    ):

        base_iri = "http://data.epo.org/linked-data/def/cpc/"
        nt_file = open(ontology_file_name_to_read, "r")
        lines = nt_file.readlines()

        csv_separator = ";;"

        content = ""
        occurrence_of_separator = 0
        for line in lines:
            matches = re.findall(";;", line)
            if len(matches) > 0:
                occurrence_of_separator += 1
            content += line.replace(".\n", "\n").replace(" ", csv_separator, 2) + "\n"

        if occurrence_of_separator != 0:
            print(f"WARNING: it is not save to use {csv_separator} as csv separator")

        # Note see cpc_nt_exploration.ipynb for explanations on why fields can be removed

        df = pd.read_csv(StringIO(content), sep=";;", header=None)
        df.columns = ["object1", "predicate", "object2"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/concordantCPC>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/concordantIPC>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/level>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/sortKey>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/symbol>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/titleXML>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/cpc/fullTitle>"]
        df = df[df.predicate != "<http://www.w3.org/2000/01/rdf-schema#label>"]
        df = df[df.predicate != "<http://www.w3.org/2004/02/skos/core#narrower>"]
        df = df[df.predicate != "<http://data.epo.org/linked-data/def/ipc/symbol>"]
        df = df[df.predicate != "<http://purl.org/dc/terms/date>"]
        df = df[df.predicate != "<http://purl.org/dc/terms/modified>"]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/ipc/") == False]

        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/A") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/B") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/C") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/D") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/E") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/F") == False]
        df = df[df.object1.str.startswith("<http://data.epo.org/linked-data/def/cpc/H") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/A") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/B") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/C") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/D") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/E") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/F") == False]
        df = df[df.object2.str.startswith("<http://data.epo.org/linked-data/def/cpc/H") == False]

        print("Predicate count after removal:")
        unique_predicates, counts = np.unique(df.predicate, return_counts=True)
        print(list(zip(unique_predicates, counts)))

        def pre_process_label(s: str) -> str:
            s = s.replace("\"", "", 1)
            s = s[::-1].replace("ne@\"", "", 1)[::-1]
            # replace invalid XML characters
            s = s.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            if s.startswith("{") and s.endswith("}"):
                s = s.replace("{", "", 1)
                s = s[::-1].replace("}", "", 1)[::-1]
            s = re.sub("\(.*\)", " ", s)
            s = re.sub("\s+", " ", s)
            if len(s) == 0:
                print("WARNING: label is empty after pre-processing")
            return s

        cpc_class_map = dict()

        df_reduced = df[(df.predicate != "<http://www.w3.org/2004/02/skos/core#hasTopConcept>") &
                        (df.predicate != "<http://www.w3.org/2004/02/skos/core#topConceptOf>") &
                        (df.predicate != "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>")]
        total_rows = len(df_reduced)
        counter = 0
        print("Starting parsing process")
        for index, row in df_reduced.iterrows():
            if row.object1 not in cpc_class_map:
                cpc_class_map[row.object1] = Clazz(row.object1)

            if row.predicate == "<http://www.w3.org/2004/02/skos/core#broader>":
                if row.object2 not in cpc_class_map:
                    cpc_class_map[row.object2] = Clazz(row.object2)
                cpc_class_map[row.object1].add_sub_class_of(row.object2)
            elif row.predicate == "<http://data.epo.org/linked-data/def/cpc/guidanceHeading>":
                additional_lables = list(
                    df[(df.object1 == row.object2) & (df.predicate == "<http://purl.org/dc/terms/title>")].object2)
                if len(additional_lables) != 1:
                    print("WARNING guidance heading has not equal to 1 title")
                is_guidance_heading = len(df[
                                              (df.object1 == row.object2) &
                                              (df.predicate == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>") &
                                              (
                                                          df.object2 == "<http://data.epo.org/linked-data/def/cpc/GuidanceHeading>")
                                              ]) > 0
                if not is_guidance_heading:
                    print("WARNING referenced guidance heading is not of type guidance heading")
                cpc_class_map[row.object1].add_label(pre_process_label(additional_lables[0]))
            elif row.predicate == "<http://purl.org/dc/terms/title>":
                cpc_class_map[row.object1].add_label(pre_process_label(row.object2))

            counter += 1
            if counter % 10000 == 0:
                print(f"progress: {counter / total_rows}")

        print("Removing all dangling concepts")
        id_pattern = re.compile("<http://data\.epo\.org/linked-data/def/cpc/.>")
        cpc_class_map = dict([(k, v) for k, v in cpc_class_map.items()
                              if re.search(id_pattern, v.idx) or len(v.subClassOf) > 0])

        max_size_label = 0
        for clazz in cpc_class_map.values():
            if len(clazz.labels) == 0:
                classification_symbol = clazz.idx[::-1].split("/")[0][1:][::-1]
                print(
                    f"WARNING {clazz.idx} has no label assigned; adding classification symbol {classification_symbol} as label")
                clazz.add_label(classification_symbol)
            for label in clazz.labels:
                max_size_label = max(max_size_label, len(label))

        print(f"max tokens in a label: {max_size_label}")

        generate_owl(preprocessed_file_to_write, list(cpc_class_map.values()), base_iri, template_path=path_to_owl_template)

    @staticmethod
    def preprocess_cpc_sub(
            full_preprocessed_cpc_ontology_filename: str,
            sub_ontology_structure_tsv_file: str,
            sub_ontology_cpc_filename_to_write: str,
            path_to_owl_template: str = None
    ):
        onto = get_ontology(full_preprocessed_cpc_ontology_filename).load()

        df_structure = pd.read_csv(sub_ontology_structure_tsv_file, sep="\t")
        depth = np.array(df_structure.Depth)
        classification_symbol = list(map(lambda x: x.replace("/", "-"), list(df_structure["Classification symbol"])))

        previous_class = None
        current_depth = -1
        stack: List[Clazz] = []
        depth_sequence_stack: List[int] = []
        classes: List[Clazz] = []
        for i in range(0, len(df_structure)):
            onto_classes = onto.search(iri=f"*{classification_symbol[i]}")
            if len(onto_classes) != 1:
                print(
                    f"WARNING: more or less than 1 classes found using classification symbol {classification_symbol[i]}")
            current_class = Clazz(onto_classes[0].iri, getattr(onto_classes[0], "label"))
            if depth[i] > current_depth:
                current_depth = depth[i]
                if previous_class is not None:
                    stack.append(previous_class)
                    depth_sequence_stack.append(depth[i - 1])
            elif depth[i] < current_depth:
                current_depth = depth[i]
                stack.pop()
                depth_sequence_stack.pop()
                parent_depth = depth_sequence_stack[-1]
                # If the following condition is the case, then the currently selected parent is not the parent
                while parent_depth >= current_depth:
                    stack.pop()
                    depth_sequence_stack.pop()
                    parent_depth = depth_sequence_stack[-1]

            if len(stack) > 0:
                parent = stack[-1]
                print(f"{classification_symbol[i]} has {parent.idx} as its parent")
                current_class.add_sub_class_of(parent.idx)
            else:
                print(f"{classification_symbol[i]} is a top-level concept")

            previous_class = current_class
            classes.append(current_class)

        generate_owl(sub_ontology_cpc_filename_to_write, classes, onto.base_iri, template_path=path_to_owl_template)

