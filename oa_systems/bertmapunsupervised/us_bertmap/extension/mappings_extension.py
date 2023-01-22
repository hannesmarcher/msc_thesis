import os
import re
from pathlib import Path

import pandas as pd

from us_bertmap.extension.bert_classifier_extend import BERTClassifierExtend
from us_bertmap.onto_box.onto_box import OntoBox
from us_bertmap.utils.shared import Shared


class MappingsExtension:
    def __init__(self, path_to_mappings_and_checkpoints: str, threshold: float, tokenizer_path: str, max_length: int,
                 string_match: bool, max_iter: int):
        self.max_iter = max_iter
        self.string_match = string_match
        self.max_length = max_length
        self.tokenizer_path = tokenizer_path
        self.threshold = threshold
        self.path_to_mappings_and_checkpoints = path_to_mappings_and_checkpoints

    def extend_maps(self, src_ob: OntoBox, tgt_ob: OntoBox):
        for file in os.listdir(self.path_to_mappings_and_checkpoints):
            if file.startswith("map."):
                candidate_limit = re.findall("map.(\d+)", file)[0]
                print(f"extending for candidate limit {candidate_limit}")

                file_to_extend = f"{self.path_to_mappings_and_checkpoints}/{file}/combined.{candidate_limit}.tsv"
                file_to_save_extended = f"{self.path_to_mappings_and_checkpoints}/{file}/extended/combined.{candidate_limit}.tsv"
                if os.path.exists(file_to_save_extended):
                    print(f"skip map extension for candidate limit {candidate_limit} as existed ...")
                    continue

                Path(f"{self.path_to_mappings_and_checkpoints}/{file}/extended/").mkdir(parents=True, exist_ok=True)

                checkpoint = self.path_to_mappings_and_checkpoints
                for file in os.listdir(self.path_to_mappings_and_checkpoints):
                    if file.startswith("checkpoint"):
                        checkpoint += f"/{file}"
                        break
                best_ckp = checkpoint.split("/")[-1]
                print(f"found best checkpoint {best_ckp}")

                bert_ex = BERTClassifierExtend(
                    src_ob=src_ob,
                    tgt_ob=tgt_ob,
                    mapping_file=file_to_extend,
                    extend_threshold=self.threshold,
                    bert_checkpoint=checkpoint,
                    tokenizer_path=self.tokenizer_path,
                    max_length=self.max_length,
                    string_match=self.string_match,
                    device_num=0
                )

                bert_ex.extend_mappings(max_iter=self.max_iter)

                exp_list = []
                for m, v in bert_ex.expansion.items():
                    src_iri, tgt_iri = m.split("\t")
                    exp_list.append((src_iri, tgt_iri, v))
                exp_df = pd.DataFrame(exp_list, columns=["Entity1", "Entity2", "Value"])

                pred_df = pd.read_csv(file_to_extend, sep="\t", na_values=Shared.na_vals, keep_default_na=False)
                extended_pred_df = pred_df.append(exp_df).reset_index(drop=True)
                extended_pred_df.to_csv(file_to_save_extended, index=False, sep="\t")
                print(f"# mappings: before={len(pred_df)} after={len(extended_pred_df)}")
