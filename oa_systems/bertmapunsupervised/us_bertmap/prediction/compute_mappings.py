import os
import re
from collections import defaultdict
from pathlib import Path
from typing import List

import pandas as pd

from us_bertmap.onto_box.onto_box import OntoBox
from us_bertmap.prediction.bert_classifier import BERTClassifierMapping


class ComputeMappings:

    def __init__(
            self,
            path_to_checkpoints: str,
            candidate_limits: List[int],
            nbest: int,
            string_match: bool,
            strategy: str,
            tokenizer_path,
            max_length: int
    ):
        self.max_length = max_length
        self.tokenizer_path = tokenizer_path
        self.strategy = strategy
        self.string_match = string_match
        self.nbest = nbest
        self.candidate_limits = candidate_limits
        self.path_to_checkpoints = path_to_checkpoints

    def compute_map(self, src_ob: OntoBox, tgt_ob: OntoBox):
        checkpoint = self.path_to_checkpoints
        for file in os.listdir(self.path_to_checkpoints):
            if file.startswith("checkpoint"):
                checkpoint += f"/{file}"
                break
        best_ckp = checkpoint.split("/")[-1]
        print(f"found best checkpoint {best_ckp}")

        for candidate_limit in self.candidate_limits:
            map_file = f"{self.path_to_checkpoints}/map.{candidate_limit}/map.{candidate_limit}.log"
            if os.path.exists(map_file):
                print(f"skip map computation for candidate limit {candidate_limit} as existed ...")
            else:
                Path(f"{self.path_to_checkpoints}/map.{candidate_limit}").mkdir(parents=True, exist_ok=True)
                mapping_computer = BERTClassifierMapping(
                    src_ob=src_ob,
                    tgt_ob=tgt_ob,
                    candidate_limit=candidate_limit,
                    bert_checkpoint=checkpoint,
                    tokenizer_path=self.tokenizer_path,
                    save_dir=f"{self.path_to_checkpoints}/map.{candidate_limit}",
                    max_length=self.max_length,
                    nbest=self.nbest,
                    string_match=self.string_match,
                    strategy=self.strategy
                )
                mapping_computer.run()
                src_df, tgt_df, combined_df = self._read_mappings_from_log(
                    f"{self.path_to_checkpoints}/map.{candidate_limit}/map.{candidate_limit}.log", keep=1
                )
                src_df.to_csv(f"{self.path_to_checkpoints}/map.{candidate_limit}/src.{candidate_limit}.tsv", sep="\t",
                              index=False)
                tgt_df.to_csv(f"{self.path_to_checkpoints}/map.{candidate_limit}/tgt.{candidate_limit}.tsv", sep="\t",
                              index=False)
                combined_df.to_csv(
                    f"{self.path_to_checkpoints}/map.{candidate_limit}/combined.{candidate_limit}.tsv", sep="\t",
                    index=False
                )

    @staticmethod
    def _read_mappings_from_log(log_path: str, keep: int = 1):
        """Read mappings from the mapping computation log"""
        with open(log_path, "r") as f:
            lines = f.readlines()
        src_maps = defaultdict(list)
        tgt_maps = defaultdict(list)
        src_pa = r"\[SRC:.*Mapping: [\(|\[]'(.+)', '(.+)', (.+)[\)|\]]\]"
        tgt_pa = r"\[TGT:.*Mapping: [\(|\[]'(.+)', '(.+)', (.+)[\)|\]]\]"
        for line in lines:
            if re.findall(src_pa, line):
                src_class, tgt_class, value = re.findall(src_pa, line)[0]
                src_maps[src_class].append((tgt_class, value))
                src_maps[src_class].sort(key=lambda x: x[1], reverse=True)
            elif re.findall(tgt_pa, line):
                tgt_class, src_class, value = re.findall(tgt_pa, line)[0]
                tgt_maps[tgt_class].append((src_class, value))
                tgt_maps[tgt_class].sort(key=lambda x: x[1], reverse=True)
        src_maps_kept = []
        tgt_maps_kept = []
        for src_class, v in src_maps.items():
            for tgt_class, value in v[:keep]:
                src_maps_kept.append((src_class, tgt_class, value))
        for tgt_class, v in tgt_maps.items():
            for src_class, value in v[:keep]:
                tgt_maps_kept.append((src_class, tgt_class, value))
        src_df = pd.DataFrame(src_maps_kept, columns=["Entity1", "Entity2", "Value"])
        tgt_df = pd.DataFrame(tgt_maps_kept, columns=["Entity1", "Entity2", "Value"])
        combined_df = src_df.append(tgt_df).drop_duplicates().dropna()
        return src_df, tgt_df, combined_df
