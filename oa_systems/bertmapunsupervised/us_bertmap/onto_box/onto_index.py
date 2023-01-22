import json
from collections import defaultdict
from itertools import chain
from typing import Iterator

from transformers import AutoTokenizer

from us_bertmap.onto_box.onto_text import OntoText


class OntoInvertedIndex:
    def __init__(
            self,
            ontotext: OntoText,
            tokenizer_path: str,
            cut: int,
            index_file: str = "",
    ):

        self.cut = cut
        self.index = defaultdict(list)
        self.tokenizer_path = tokenizer_path
        self.ontotext = ontotext
        self.tokenizer = None

        if index_file:
            self.load_index(index_file)
        else:
            self.init_tokenizer(tokenizer_path)
            self.construct_index(cut)

    def __repr__(self):
        return f"<OntoInvertedIndex num_entries={len(self.index)} cut={self.cut} tokenizer_path={self.tokenizer_path}>"

    def init_tokenizer(self, tokenizer_path: str) -> None:
        """Set or change the tokenizer used for creating the Index,
        note that when loading, the tokenizer is not loaded by default,
        but in the OntoBox class, the tokenizer info is stored
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    def tokenize(self, texts) -> Iterator:
        return chain.from_iterable([self.tokenizer.tokenize(text) for text in texts])

    def construct_index(self, cut: int) -> None:
        """Create Inverted Index with sub-word tokens

        Args:
            cut (int): ignore sub-word tokens of length <= cut
        """
        self.index = defaultdict(list)
        for cls_iri, text_dict in self.ontotext.texts.items():
            tokens = self.tokenize(text_dict["label"])
            for token in tokens:
                if len(token) > cut:
                    self.index[token].append(self.ontotext.class2idx[cls_iri])

    def save_index(self, index_file: str) -> None:
        with open(index_file, "w") as f:
            json.dump(self.index, f, indent=4, separators=(",", ": "), sort_keys=True)

    def load_index(self, index_file: str) -> None:
        with open(index_file, "r") as f:
            self.index = json.load(f)
