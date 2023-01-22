import re
from typing import List

import numpy as np
import pandas as pd
import pywikibot
from rdflib import Graph

from ontology_preprocessing.clazz import Clazz
from ontology_preprocessing.owl_generator import generate_owl


class CSOPreprocessor:

    @staticmethod
    def preprocess_cso(
            filename_to_read: str,
            filename_to_write: str,
            categories_to_consider: List[str] = None,
            path_to_owl_template: str = None):

        if categories_to_consider is None:
            categories_to_consider = []

        base_iri = "https://cso.kmi.open.ac.uk/topics/"

        g = Graph()

        skos_file = open(filename_to_read, "r")
        lines = skos_file.readlines()
        data = ""
        for line in lines:
            if re.match("lang=[^en]", line):
                print(f"WARNING: other language than english used: {line}")
            data += line

        g.parse(data=data, format="application/rdf+xml")

        # Preparation
        all_subj = []
        all_preds = []
        all_obj = []
        for subj, pred, obj in g:
            all_subj.append(str(subj).strip())
            all_obj.append(str(obj).strip())
            all_preds.append(str(pred).strip())

        df = pd.DataFrame(data={"subject": all_subj, "predicate": all_preds, "object": all_obj})

        print("All predicates:")
        print(np.unique(df.predicate))

        # Filtering:
        df = df[(df.predicate != "http://cso.kmi.open.ac.uk/schema/cso#contributesTo") &
                (df.predicate != "http://schema.org/relatedLink")]

        cso_class_map = dict()

        for subject in np.unique(df[df.predicate == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"].subject):
            cso_class_map[subject] = Clazz(subject)

        df = df[df.predicate != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]

        # Check if each subject has a type:
        #for subject in np.unique(df.subject):
        #    if subject not in cso_class_map.keys():
        #        print(f"{subject} has no type")
        # There are topics that are have no type; including these would lead to many loose top-level concepts

        def get_class(url):
            if url in cso_class_map:
                return cso_class_map[url]
            return Clazz("Dummy")

        #wikidata_prefix = "https://www.wikidata.org/wiki/Special:EntityData/"
        # Initializing the wikidata repository
        wikidata_repo =  pywikibot.Site("wikidata", "wikidata").data_repository()
        total_rows = len(df)
        counter = 0
        for index, row in df.iterrows():
            if row.predicate == "http://cso.kmi.open.ac.uk/schema/cso#superTopicOf":
                get_class(row.object).add_sub_class_of(row.subject)
            elif row.predicate == "http://cso.kmi.open.ac.uk/schema/cso#relatedEquivalent" or row.predicate == "http://cso.kmi.open.ac.uk/schema/cso#preferentialEquivalent":
                get_class(row.subject).add_equivalent_class(row.object)
            elif row.predicate == "http://www.w3.org/2000/01/rdf-schema#label":
                get_class(row.subject).add_label(row.object)
            elif row.predicate == "http://www.w3.org/2002/07/owl#sameAs":
                dbpedia_url = "http://dbpedia.org/resource"
                wikidata_url = "http://www.wikidata.org/entity"
                yago_url = "http://yago-knowledge.org/resource"
                if wikidata_url in row.object:
                    idx = row.object[::-1].split("/", 1)[0][::-1]
                    item = pywikibot.ItemPage(wikidata_repo, idx)
                    if item.exists():
                        try:
                            item_dict = item.get()
                            get_class(row.subject).add_label(item_dict["labels"]["en"])
                        except pywikibot.exceptions.IsRedirectPageError:
                            print(f"WARNING: IsRedirectPageError for {row.object}")
                    else:
                            print(f"WARNING: {row.object} not existing")
                elif dbpedia_url in row.object:
                    idx = row.object[::-1].split("/", 1)[0][::-1]
                    get_class(row.subject).add_label(idx.replace("_", " "))
                elif yago_url in row.object and (yago_url + "/ISO") not in row.object:
                    idx = row.object[::-1].split("/", 1)[0][::-1]
                    get_class(row.subject).add_label(idx.replace("_", " "))

            counter += 1
            if counter % 1000 == 0:
                print(f"progress: {counter / total_rows}")

        max_size_label = 0
        for key, value in cso_class_map.items():
            max_size_label = max(np.max(np.array([len(l) for l in value.labels])), max_size_label)

        print(f"max tokens in a label: {max_size_label}")

        # Propagate each label to all the equivalent classes
        label_was_added = False
        while not label_was_added:
            for current_class in cso_class_map.values():
                for equivalent_class in current_class.equivalent:
                    equivalent_class = cso_class_map[equivalent_class]
                    for label in current_class.labels:
                        if label not in equivalent_class.labels:
                            label_was_added = True
                            equivalent_class.add_label(label)

        if len(categories_to_consider) > 0:
            print("Allowing only classes with " + str(categories_to_consider) + " as super classes")

            def is_relevant(id: str) -> bool:
                if id in categories_to_consider:
                    return True
                cso_class = cso_class_map[id]
                for super_class_id in cso_class.subClassOf:
                    if is_relevant(super_class_id):
                        return True

                return False


            to_delete = []
            for key in cso_class_map.keys():
                # Do not check the entry point of the ontology
                if key == "https://cso.kmi.open.ac.uk/topics/computer_science":
                    continue
                if not is_relevant(key):
                    to_delete.append(key)

            cso_class_map = {k: v for k, v in cso_class_map.items() if k not in to_delete}
            for value in cso_class_map.values():
                value.subClassOf = [c for c in value.subClassOf if c not in to_delete]

        print(f"{len(cso_class_map)} classes")

        generate_owl(filename_to_write, list(cso_class_map.values()), base_iri, template_path=path_to_owl_template)