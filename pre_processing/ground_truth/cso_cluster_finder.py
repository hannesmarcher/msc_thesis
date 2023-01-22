"""
This class finds clusters based on attributes.
For example, assume class A1 has label "B1" and class A2 has also label "B1", then both classes would belong to the same cluster.
This clustering is useful for the construction of the ground truth as it prevents overlooking of equivalent classes.
"""
from typing import List

from owlready2 import *


class CSOClusterFinder:
    @staticmethod
    def get_clusters(cso_filename: str) -> List[List[str]]:
        onto = get_ontology(f"file://{cso_filename}").load()
        properties = ["label"]

        values_to_class_dict = dict()
        for clazz in onto.classes():
            assert type(clazz) is entity.ThingClass
            all_values = set([])
            for prop in properties:
                values = getattr(clazz, prop)
                assert type(values) is IndividualValueList
                for value in values:
                    all_values.add(value)

            all_values_frozen = frozenset(all_values)
            if all_values_frozen in values_to_class_dict:
                values_to_class_dict[all_values_frozen].append(clazz.iri)
            else:
                values_to_class_dict[all_values_frozen] = [clazz.iri]

        lines = []
        for class_list in values_to_class_dict.values():
            lines.append([str(clazz).replace("https://cso.kmi.open.ac.uk/topics/", "") for clazz in class_list])

        return lines