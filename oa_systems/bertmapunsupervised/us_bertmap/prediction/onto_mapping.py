"""
Mapping Generation superclass on using some kind of normalized distance metric or classifier (from fine-tuned BERT):

   Prelimniary Algorithm (One-side-fixed Search):

        Compute the *Value between each source-target entity pair where Value is defined by:
           Dist = norm_distance(class1, class2)
           Value = norm_similarity(class1, class2)

        [Fix the source side]
            For each source class (class1), pick the target class (class2) according to the min(Dist) or max(Value)

        [Fix the target side]
            For each target class (class2), pick the source class (class1) according to the min(Dist) opr max(Value)

        Remove the duplicates

    Note: The search space can be reduced by setting up a candidate selection algorithm.
    Current supported candidate selection: [Subword-level Inverted Index, ]
"""

import time
from typing import Tuple

from us_bertmap.onto_box.onto_box import OntoBox
from us_bertmap.utils.helpers import log_print


class OntoMapping:
    def __init__(
            self,
            src_ob: OntoBox,
            tgt_ob: OntoBox,
            candidate_limit: int = 50,
            save_dir: str = "",
    ):

        self.src_ob = src_ob
        self.tgt_ob = tgt_ob
        self.candidate_limit = candidate_limit
        self.save_dir = save_dir
        self.log_print = lambda info: log_print(
            info, f"{self.save_dir}/map.{self.candidate_limit}.log"
        )
        self.start_time = None

    def run(self) -> None:
        """Run the computation of mapping calculation"""
        t_start = time.time()
        self.log_print(f"Candidate Limit: {self.candidate_limit}")
        self.alignment("SRC")
        t_src = time.time()
        self.log_print(f"the program time for computing src2tgt mappings is :{t_src - t_start}")
        self.alignment("TGT")
        t_tgt = time.time()
        self.log_print(f"the program time for computing tgt2src mappings is :{t_tgt - t_src}")
        t_end = time.time()
        self.log_print(f"the overall program time is :{t_end - t_start}")

    def from_to_config(self, flag: str = "SRC") -> Tuple[OntoBox, OntoBox]:
        """switch source and target OntoBox objects according to flag"""
        assert flag == "SRC" or flag == "TGT"
        if flag == "SRC":
            from_ob, to_ob = self.src_ob, self.tgt_ob
        else:
            from_ob, to_ob = self.tgt_ob, self.src_ob
        return from_ob, to_ob

    def alignment(self, flag: str = "SRC") -> None:
        """Fixed one-side ontology alignment"""
        raise NotImplementedError
