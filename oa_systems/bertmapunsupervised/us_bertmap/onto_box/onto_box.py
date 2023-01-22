import ast
import math
import os
import re
from collections import defaultdict
from pathlib import Path
from shutil import copy2
from typing import List

from owlready2 import get_ontology, ThingClass

from us_bertmap.onto_box.onto_index import OntoInvertedIndex
from us_bertmap.onto_box.onto_text import OntoText
from us_bertmap.utils.helpers import banner


class OntoBox:
    def __init__(
            self,
            onto_iri_abbr: str,
            onto_file: str,
            synonym_properties: List[str],
            tokenizer_path: str,
            cut: int = 0,
            from_saved: bool = False,
    ):

        # load owlready2 ontology and assign attributes
        self.onto_file = onto_file
        self.onto = get_ontology(f"file://{onto_file}").load()

        if not from_saved:
            self.onto_text = OntoText(
                self.onto,
                iri_abbr=onto_iri_abbr,
                synonym_properties=synonym_properties
            )
            self.onto_index = OntoInvertedIndex(self.onto_text, tokenizer_path, cut=cut)
        else:
            pass  # use from_saved at a later stage

    def __repr__(self):
        report = f"<OntoBox> onto='{self.onto.name}.owl' iri='{self.onto.base_iri}'>\n"
        report += f"\t{self.onto_text}" + "\n"
        report += f"\t{self.onto_index}" + "\n"
        report += "</OntoBox>\n"
        return report

    def save(self, save_dir) -> None:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        copy2(self.onto_file, save_dir)
        self.onto_text.save_classtexts(save_dir + f"/{self.onto.name}.ctxt.json")
        self.onto_index.save_index(save_dir + f"/{self.onto.name}.ind.json")
        with open(save_dir + "/info", "w") as f:
            f.write(str(self))

    def select_candidates(self, classtexts: List[str], candidate_limit: int = 50) -> List[str]:
        """Given the texts associated to a class, select a set of
           classes in current (self) ontology according to IDF; this
           set is likely to contain a class aligned to the class that
           possesses the input classtexts.

        Args:
            classtexts (List[str]): list of texts associated to a class to be aligned
            candidate_limit (int, optional): upper limit of the candidate pool. Defaults to 50.
        """
        candidate_pool = defaultdict(lambda: 0)
        tokens = self.onto_index.tokenize(classtexts)
        D = len(self.onto_text.class2idx)  # num of "documents" (classes)
        for tk in tokens:
            potential_candidates = self.onto_index.index.setdefault(
                tk, []
            )  # each token is associated with some classes
            if not potential_candidates:
                continue
            # We use idf instead of tf because the text for each class is of different length, tf is not a fair measure
            # inverse document frequency: with more classes to have the current token tk, the score decreases
            idf = math.log10(D / len(potential_candidates))
            for class_id in potential_candidates:
                candidate_pool[class_id] += idf  # each candidate class is scored by sum(idf)
        candidate_pool = list(
            sorted(candidate_pool.items(), key=lambda item: item[1], reverse=True)
        )[:candidate_limit]
        selected_classes = [self.onto_text.idx2class[c[0]] for c in candidate_pool]
        show = min(candidate_limit, 2)
        banner(f"select {len(candidate_pool)} candidates", sym="^")
        print(f"e.g. {selected_classes[:show]}")
        return selected_classes

    @classmethod
    def from_saved(cls, save_dir):
        """Create an OntoBox instance from data files in specified formats"""
        # check and load onto data files
        onto_file = []
        classtexts_file = []
        inv_index_file = []
        info_file = []
        for file in os.listdir(save_dir):
            if file.endswith(".owl"):
                onto_file.append(file)
            elif file.endswith(".ctxt.json"):
                classtexts_file.append(file)
            elif file.endswith(".ind.json"):
                inv_index_file.append(file)
            elif file == "info":
                info_file.append(file)
            else:
                print(f"[ERROR] invalid file detected: {file}")
                return
        if len(onto_file) != 1 or len(classtexts_file) != 1 or len(inv_index_file) != 1:
            print(f"[ERROR] multiple data files detected")
            return
        with open(f"{save_dir}/{info_file[0]}", "r") as f:
            lines = f.readlines()
            iri_abbr = re.findall(r"abbr=\'(.+?)\'", lines[1])[0]
            properties = ast.literal_eval(re.findall(r"prop=(\[.+])", lines[1])[0])
            cut = int(re.findall(r"cut=([0-9]+)", lines[2])[0])
            tokenizer_path = re.findall(r"tokenizer_path=(.+)>", lines[2])[0]
        # construct the OntoBox instance
        print(f"found files of correct formats, trying to load ontology data from {save_dir}")
        ontobox = cls(
            iri_abbr,
            f"{save_dir}/{onto_file[0]}",
            properties,
            tokenizer_path,
            from_saved=True
        )
        ontobox.onto_text = OntoText(
            ontobox.onto, iri_abbr, properties, f"{save_dir}/{classtexts_file[0]}"
        )
        ontobox.onto_index = OntoInvertedIndex(
            cut=cut, index_file=f"{save_dir}/{inv_index_file[0]}", tokenizer_path=tokenizer_path,
            ontotext=ontobox.onto_text
        )
        ontobox.onto_index.init_tokenizer(tokenizer_path)
        return ontobox

    def create_class2depth(self, strategy: str = "max") -> None:
        assert strategy == "max" or strategy == "min"
        class2depth = dict()
        depth_func = getattr(self, "depth_" + strategy)
        for cl in self.onto.classes():
            cl_iri_abbr = self.onto_text.abbr_entity_iri(cl.iri)
            class2depth[cl_iri_abbr] = depth_func(cl)
        setattr(self, f"class2depth_{strategy}", class2depth)

    @staticmethod
    def super_classes(cl: ThingClass) -> List[ThingClass]:
        supclasses = list()
        for supclass in cl.is_a:
            # ignore the root class Thing
            if type(supclass) == ThingClass and supclass.name != "Thing":
                supclasses.append(supclass)
        return supclasses
