import os
from pathlib import Path
from typing import Optional, List

from us_bertmap.onto_box.onto_box import OntoBox


class OntoBoxLoader:
    def __init__(self,
                 task_directory: str,
                 source_onto_path: str,
                 target_onto_path: str,
                 source_onto_abbr: str,
                 target_onto_abbr: str,
                 tokenizer_path: str,
                 synonym_properties: Optional[List[str]] = None):
        if synonym_properties is None:
            synonym_properties = ["label"]
        self.synonym_properties = synonym_properties
        self.tokenizer_path = tokenizer_path
        self.target_onto_abbr = target_onto_abbr
        self.source_onto_abbr = source_onto_abbr
        self.target_onto_path = target_onto_path
        self.source_onto_path = source_onto_path
        self.task_directory = task_directory
        self.src_onto_box = None
        self.tgt_onto_box = None

    def prepare_data(self):
        src_abbrv, tgt_abbrv = self.source_onto_abbr, self.target_onto_abbr
        src_path, tgt_path = self.source_onto_path, self.target_onto_path
        task_dir = self.task_directory

        # load the src ontology data files if already created
        if os.path.exists(task_dir + "/src.onto"):
            print("source onto already exists, trying to load source pre-computed source ontology")
            self.src_onto_box = OntoBox.from_saved(task_dir + "/src.onto")
        else:
            Path(task_dir + "/src.onto").mkdir(parents=True, exist_ok=True)

        # create the data files if not existed or missing
        if not self.src_onto_box:
            self.src_onto_box = OntoBox(
                src_abbrv,
                src_path,
                self.synonym_properties,
                self.tokenizer_path,
                0,  # TODO extract cut?
            )
            self.src_onto_box.save(task_dir + "/src.onto")
        print(self.src_onto_box)

        # load the tgt ontology data files if already created
        if os.path.exists(task_dir + "/tgt.onto"):
            print("target onto already exists, trying to load source pre-computed source ontology")
            self.tgt_onto_box = OntoBox.from_saved(task_dir + "/tgt.onto")
        else:
            Path(task_dir + "/tgt.onto").mkdir(parents=True, exist_ok=True)
        # create the data files if not existed or missing
        if not self.tgt_onto_box:
            self.tgt_onto_box = OntoBox(
                tgt_abbrv,
                tgt_path,
                self.synonym_properties,
                self.tokenizer_path,
                0,  # TODO extract cut?
            )
            self.tgt_onto_box.save(task_dir + "/tgt.onto")
        print(self.tgt_onto_box)
