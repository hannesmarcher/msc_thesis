"""
Corpora class for handling all kinds of sub-corpora involved in an alignment task
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from us_bertmap.corpus.intra_corpus import IntraOntoCorpus
from us_bertmap.corpus.merged_corpus import MergedOntoCorpus
from us_bertmap.onto_box.onto_box import OntoBox
from us_bertmap.utils.helpers import uniqify


class OntoAlignCorpora:
    def __init__(
            self,
            src_ob: Optional[OntoBox] = None,
            tgt_ob: Optional[OntoBox] = None,
            train_map_ratio: float = 0.2,
            val_map_ratio: float = 0.1,
            test_map_ratio: float = 0.7,
            sample_rate: int = 10,
            io_soft_neg_rate: int = 1,
            io_hard_neg_rate: int = 1,
            depth_threshold: Optional[int] = None,
            depth_strategy: Optional[str] = "max",
    ):
        # attributes for extracting label data
        self.tra_map_ratio = train_map_ratio
        self.val_map_ratio = val_map_ratio
        self.test_map_ratio = test_map_ratio
        self.io_soft_neg_rate = io_soft_neg_rate
        self.io_hard_neg_rate = io_hard_neg_rate
        # intra-onto copora merged
        self.src_io = IntraOntoCorpus(src_ob, sample_rate, depth_threshold, depth_strategy)
        self.tgt_io = IntraOntoCorpus(tgt_ob, sample_rate, depth_threshold, depth_strategy)
        self.src_tgt_io = MergedOntoCorpus(self.src_io, self.tgt_io)

    def __repr__(self):
        report = "Not computed"
        return report

    def save(self, save_dir) -> None:
        Path(save_dir + "/refs").mkdir(parents=True, exist_ok=True)
        Path(save_dir + "/corpora").mkdir(parents=True, exist_ok=True)
        # save the corpora
        self.src_tgt_io.save_corpus(save_dir + "/corpora/io.corpus.json")
        # save the corpora info
        with open(save_dir + "/corpora/info", "w") as f:
            f.write(str(self))

    @staticmethod
    def save_maps(loaded_maps, save_file) -> None:
        maps = [(mapping.split("\t")[0], mapping.split("\t")[1], 1.0) for mapping in loaded_maps]
        pd.DataFrame(maps, columns=["Entity1", "Entity2", "Value"]).to_csv(
            save_file, sep="\t", index=False
        )

    def unsupervised_data(self) -> Dict[str, List[str]]:
        us_io_train, us_io_val, us_io_train_ids, us_io_val_ids = self.src_tgt_io.train_val_split(
            val_ratio=0.2, soft_neg_rate=self.io_soft_neg_rate, hard_neg_rate=self.io_hard_neg_rate
        )
        us_train_with_ids = uniqify(us_io_train + us_io_train_ids)
        us_val_with_ids = uniqify(us_io_val + us_io_val_ids)
        random.shuffle(us_io_train)
        random.shuffle(us_train_with_ids)
        random.shuffle(us_io_val)
        random.shuffle(us_val_with_ids)
        us_data = {
            "train": us_io_train,
            "train+": us_train_with_ids,
            "val": us_io_val,
            "val+": us_val_with_ids,
        }
        return us_data
