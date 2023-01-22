import re

import numpy as np
from rdflib import Graph

from ontology_preprocessing.clazz import Clazz
from ontology_preprocessing.owl_generator import generate_owl


class CCSPreprocessor:

    @staticmethod
    def preprocess_ccs(
            skos_filename: str,
            filename_to_write: str,
            categories_to_consider=None,
            path_to_owl_template: str = None):
        if categories_to_consider is None:
            categories_to_consider = []
        base_iri = "https://dl.acm.org/ccs/topics/"  # arbitrarily chosen - in the skos file there is no base iri given
        skos_file = open(skos_filename, "r")
        lines = skos_file.readlines()
        data = ""
        for line in lines:
            if re.match("lang=[^en]", line):
                print(f"WARNING: other language than english used: {line}")
            # Somehow blank nodes are introduced if lang=en is used, and the text of the label cannot be retrieved
            data += line.replace(" lang=\"en\"", "")

        g = Graph()
        g.parse(data=data, format="application/rdf+xml")

        # Preparation
        all_preds = []
        for subj, pred, obj in g:
            all_preds.append(pred)

        print("The following predicates exist:")
        unique_preds = np.unique(np.array(all_preds))
        for preds in unique_preds:
            print(preds)

        # Collecting all classes
        all_classes = []
        for subj, pred, obj in g:
            if str(pred) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(
                    obj) == "http://www.w3.org/2004/02/skos/core#Concept":
                all_classes.append(str(subj))

        max_size_label = 0
        ccs_class_map = dict()
        for subj, pred, obj in g:
            if pred[-len("#prefLabel"):] == "#prefLabel":
                # Ensure that each concept has only one label
                if str(subj) in ccs_class_map:
                    print(f"WARNING: class: {str(subj)} already existed")
                label = str(obj)
                max_size_label = max(max_size_label, len(label))
                ccs_class_map[str(subj)] = Clazz(idx=str(subj), labels={label})

        # Assert that each class has a label
        assert len(all_classes) == len(ccs_class_map)

        print(f"max tokens in a label: {max_size_label}")

        for subj, pred, obj in g:
            if pred[-len("#broader"):] == "#broader":
                ccs_class_map[str(subj)].add_sub_class_of(ccs_class_map[str(obj)].idx)

        if len(categories_to_consider) > 0:
            print("Allowing only classes with " + str(categories_to_consider) + " as super classes")

            def is_relevant(id: str) -> bool:
                if id in categories_to_consider:
                    return True
                ccs_class = ccs_class_map[id]
                for super_class_id in ccs_class.subClassOf:
                    if is_relevant(super_class_id):
                        return True

                return False


            to_delete = []
            for key in ccs_class_map.keys():
                if not is_relevant(key):
                    to_delete.append(key)

            ccs_class_map = {k: v for k, v in ccs_class_map.items() if k not in to_delete}
            for value in ccs_class_map.values():
                value.subClassOf = [c for c in value.subClassOf if c not in to_delete]

            # Count if there are duplicate labels - useful to know for ground truth construction
            #   since, in case of no duplication, the labels can be used instead of the ids for the reference alignment
            # We have already checked above that each class has exactly one label, therefore:
            unique_labels, label_count = np.unique([list(c.labels)[0] for c in ccs_class_map.values()], return_counts=True)
            label_ids_more_one_occurrence = np.where(label_count > 1)
            for label, count in list(zip(unique_labels[label_ids_more_one_occurrence], label_count[label_ids_more_one_occurrence])) :
                print(f"Note: {label} occurs {count} times")

        print(f"{len(ccs_class_map)} classes")

        generate_owl(filename_to_write, classes=list(ccs_class_map.values()), base_iri=base_iri, template_path=path_to_owl_template)