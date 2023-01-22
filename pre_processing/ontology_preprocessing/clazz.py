from typing import Set


class Clazz:

    def __init__(self, idx: str, labels: Set[str] = None) -> None:
        if labels is None:
            labels = set([])
        self.idx = idx
        self.labels: Set[str] = labels
        self.subClassOf: Set[str] = set([])
        self.equivalent: Set[str] = set([])

    def add_label(self, label: str):
        if label.lower() not in self.labels:
            self.labels.add(label.lower())

    def add_sub_class_of(self, parent: str):
        self.subClassOf.add(parent)

    def add_equivalent_class(self, equivalent_class: str):
        self.equivalent.add(equivalent_class)