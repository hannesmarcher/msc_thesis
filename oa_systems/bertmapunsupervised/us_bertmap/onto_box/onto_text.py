import json
from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import List, Iterable, Dict

from owlready2 import Ontology, ThingClass, IndividualValueList

from us_bertmap.utils.helpers import banner
from us_bertmap.utils.helpers import uniqify


class OntoText:

    def __init__(
            self,
            onto: Ontology,
            iri_abbr: str,
            synonym_properties: List[str],
            classtexts_file: str = "",
    ):

        self.onto = onto
        self.name = self.onto.name
        self.iri = self.onto.base_iri
        self.synonym_properties = synonym_properties
        self.iri_abbr = iri_abbr

        # create or load texts associated to each class
        self.num_texts = 0
        self.texts = defaultdict(lambda: defaultdict(list))
        if not classtexts_file:
            self.extract_classtexts(self.synonym_properties)
        else:
            self.load_classtexts(classtexts_file)

        # assign indices to classes
        self.class2idx = dict()
        self.idx2class = dict()
        i = 0
        # TODO is it really guaranteed that the order is always the same?
        #       - otherwise the pre-computed inverted index is wrong
        for class_iri, _ in self.texts.items():
            self.class2idx[class_iri] = i
            self.idx2class[i] = class_iri
            i += 1

    def __repr__(self):
        iri_abbr = self.iri_abbr.replace(":", "")
        return f"<OntoText abbr='{iri_abbr}' num_classes={len(self.class2idx)} num_texts={self.num_texts} prop={self.synonym_properties}>"

    def extract_classtexts(self, synonym_properties) -> None:
        self.num_texts = 0
        self.texts = defaultdict(lambda: defaultdict(list))
        for cl in self.onto.classes():
            cl_iri_abbr = self.abbr_entity_iri(cl.iri)
            for prop in synonym_properties:
                # regard every synonym text as a label
                self.texts[cl_iri_abbr]["label"] += self._preprocess_classtexts(cl, prop)
            self.texts[cl_iri_abbr]["label"] = uniqify(self.texts[cl_iri_abbr]["label"])

            ##########################################
            # Custom Code
            ##########################################
            if len(self.texts[cl_iri_abbr]["label"]) == 0:
                artificial_label = cl_iri_abbr.split("#")[-1].lower().replace("_", " ")
                print(f"WARNING: {cl_iri_abbr} has no label")
                print(f"\tusing {artificial_label} as label")
                self.texts[cl_iri_abbr]["label"] += artificial_label
            ##########################################
            # End Code Changes
            ##########################################

            self.num_texts += len(self.texts[cl_iri_abbr]["label"])

    def abbr_entity_iri(self, entity_iri: str) -> str:

        if self.iri in entity_iri:
            return entity_iri.replace(self.iri, self.iri_abbr + ":")

        # change nothing if no abbreviation available
        return entity_iri

    def _preprocess_classtexts(self, cl: ThingClass, prop: str) -> List[str]:
        """Preprocessing the texts of a class given by a particular property including
        underscores removal and lower-casing.

        Args:
            cl : class entity
            prop (str): name of the property, e.g. "label"

        Returns:
            list: cleaned and uniqified class-texts
        """
        raw_texts = getattr(cl, prop)
        assert type(raw_texts) is IndividualValueList
        cleaned_texts = [txt.lower().replace("_", " ") for txt in
                         raw_texts]  # TODO more preprocessing, e.g. stop word removal, etc.
        return uniqify(cleaned_texts)

    def save_classtexts(self, classtexts_file: str) -> None:
        # do not sort keys otherwise class2idx and idx2class will be mis-used later
        with open(classtexts_file, "w") as f:
            json.dump(self.texts, f, indent=4, separators=(",", ": "))

    def load_classtexts(self, classtexts_file: str) -> None:
        with open(classtexts_file, "r") as f:
            self.texts = json.load(f)
        # compute number of texts
        self.num_texts = 0
        for td in self.texts.values():
            for txts in td.values():
                self.num_texts += len(txts)

    def labels_iterator(
            self, selected_classes: List[str], label_size: int
    ) -> Iterable[Dict[str, Dict]]:
        """
        Args:
            selected_classes (List[str])
            label_size (int): the number for stopping adding more classes into batch,
            once the number of labels in this batch exceeds this number for the first time,
            it will be added to the batch list

        Yields:
            dict: dictionary that stores a batch of (class-iri, class-text) pairs
            according to specified label size (so number of classes in the batch varies).
        """
        batches = []
        batch = OrderedDict()
        label_num = 0
        total_class_num = 0
        class_num = 0
        for i in range(len(selected_classes)):
            cl = selected_classes[i]
            text_dict = deepcopy(self.texts[cl])
            # finish a batch when there is something in the batch AND
            # addining the next class'sl labels will exceed size limit
            to_be_full = label_num + len(text_dict["label"]) >= label_size
            if batch and to_be_full:
                batches.append(deepcopy(batch))
                batch = OrderedDict()
                total_class_num += class_num
                class_num = 0
                label_num = 0
            batch[cl] = text_dict  # adding the labels into batch
            class_num += 1
            label_num += len(text_dict["label"])
            # don't forget the last class
            if i == len(selected_classes) - 1:
                batches.append(deepcopy(batch))
                total_class_num += class_num
        # simple test to secure the algorithm is right
        assert total_class_num == len(selected_classes)
        batch_lens = [len(b) for b in batches]
        assert sum(batch_lens) == len(selected_classes)
        banner(f"form {len(batch_lens)} batches")
        return batches

    def expand_entity_iri(self, entity_iri_abbr: str) -> str:
        """onto_iri#fragment <= onto_prefix:fragment"""
        if entity_iri_abbr.startswith(self.iri_abbr):
            return entity_iri_abbr.replace(self.iri_abbr + ":", self.iri)

        print(f"WARNING: {entity_iri_abbr} has no known prefix")
        return entity_iri_abbr
