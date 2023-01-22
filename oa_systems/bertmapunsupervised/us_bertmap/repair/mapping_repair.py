import os
import re
import subprocess
from pathlib import Path

import pandas as pd

from us_bertmap.extension.bert_classifier_extend import BERTClassifierExtend
from us_bertmap.onto_box.onto_box import OntoBox
from us_bertmap.utils.shared import Shared


class MappingRepair:

    def __init__(
            self,
            path_to_source_onto: str,
            path_to_target_onto: str,
            source_ob: OntoBox,
            target_ob: OntoBox,
            path_to_mappings_and_checkpoints: str,
            path_to_logmap_jar: str,
            threshold: float
    ):
        self.path_to_source_onto = path_to_source_onto
        self.path_to_target_onto = path_to_target_onto

        for file in os.listdir(path_to_source_onto):
            if file.endswith(".owl"):
                self.path_to_source_onto += f"/{file}"
                break

        for file in os.listdir(path_to_target_onto):
            if file.endswith(".owl"):
                self.path_to_target_onto += f"/{file}"
                break

        self.target_ob = target_ob
        self.source_ob = source_ob
        self.path_to_logmap_jar = path_to_logmap_jar
        self.path_to_mappings_and_checkpoints = path_to_mappings_and_checkpoints
        self.threshold = threshold

    def repair_maps(self):
        for file in os.listdir(self.path_to_mappings_and_checkpoints):
            if file.startswith("map."):
                candidate_limit = re.findall("map.(\d+)", file)[0]
                file_to_repair = f"{self.path_to_mappings_and_checkpoints}/{file}/extended/combined.{candidate_limit}.tsv"
                path_to_repaired_directory = f"{self.path_to_mappings_and_checkpoints}/{file}/repaired"
                file_to_save_repaired = f"{path_to_repaired_directory}/combined.{candidate_limit}.tsv"
                print(f"repairing extended map for candidate limit {candidate_limit}")

                if os.path.exists(file_to_save_repaired):
                    print(f"skip map repair for candidate limit {candidate_limit} as existed ...")
                    continue

                Path(path_to_repaired_directory).mkdir(parents=True, exist_ok=True)
                formatted_file_path = self._repair_formatting(file_to_repair, repair_threshold=self.threshold)

                # apply java commands of LogMap DEBUGGER
                repair_command = (
                        f"java -jar {os.path.abspath(self.path_to_logmap_jar)} DEBUGGER "
                        + f"file:{os.path.abspath(self.path_to_source_onto)} file:{os.path.abspath(self.path_to_target_onto)} TXT {os.path.abspath(formatted_file_path)} {os.path.abspath(path_to_repaired_directory)} false true"
                )
                repair_process = subprocess.Popen(repair_command.split(" "))
                try:
                    _, _ = repair_process.communicate(timeout=120)
                except subprocess.TimeoutExpired:
                    repair_process.kill()
                    _, _ = repair_process.communicate()
                self._eval_formatting(f"{path_to_repaired_directory}/mappings_repaired_with_LogMap.tsv",
                                      candidate_limit)

    def _repair_formatting(self, file_to_repair: str, repair_threshold: float):
        map_dict = BERTClassifierExtend.read_mappings_to_dict(file_to_repair, threshold=repair_threshold)
        lines = []
        for m in map_dict.keys():
            src_iri, tgt_iri = m.split("\t")
            src_iri = self.source_ob.onto_text.expand_entity_iri(src_iri)
            tgt_iri = self.target_ob.onto_text.expand_entity_iri(tgt_iri)
            value = map_dict[m]
            lines.append(f"{src_iri}|{tgt_iri}|=|{value}|CLS\n")
        formatted_file = file_to_repair.replace(".tsv", "-logmap_format.txt")
        with open(formatted_file, "w") as f:
            f.writelines(lines)
        return formatted_file

    def _eval_formatting(self, repaired_map_file_tsv, candidate_limit):
        repaired_df = pd.read_csv(
            repaired_map_file_tsv,
            sep="\t",
            names=["Entity1", "Entity2", "Value"],
            na_values=Shared.na_vals,
            keep_default_na=False,
        )
        repaired_df["Entity1"] = repaired_df["Entity1"].apply(
            lambda iri: self.source_ob.onto_text.abbr_entity_iri(iri)
        )
        repaired_df["Entity2"] = repaired_df["Entity2"].apply(
            lambda iri: self.target_ob.onto_text.abbr_entity_iri(iri)
        )
        repaired_df.to_csv(
            repaired_map_file_tsv.replace(
                "mappings_repaired_with_LogMap.tsv", f"combined.{candidate_limit}.tsv"
            ),
            index=False,
            sep="\t",
        )
