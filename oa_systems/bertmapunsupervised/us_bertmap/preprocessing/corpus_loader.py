from us_bertmap.corpus.ontology_align_corpora import OntoAlignCorpora
from us_bertmap.onto_box.onto_box import OntoBox


class CorpusLoader():
    def __init__(
            self,
            src_ob: OntoBox,
            tgt_ob: OntoBox,
            train_map_ratio: float = 0.2,
            val_map_ratio: float = 0.1,
            test_map_ratio: float = 0.7,
            sample_rate: int = 10,
            io_soft_neg_rate: int = 1,
            io_hard_neg_rate: int = 1,
            depth_threshold: int = None,
            depth_strategy: str = "max"
    ):
        self.depth_strategy = depth_strategy
        self.depth_threshold = depth_threshold
        self.io_hard_neg_rate = io_hard_neg_rate
        self.io_soft_neg_rate = io_soft_neg_rate
        self.sample_rate = sample_rate
        self.test_map_ratio = test_map_ratio
        self.val_map_ratio = val_map_ratio
        self.train_map_ratio = train_map_ratio
        self.tgt_ob = tgt_ob
        self.src_ob = src_ob
        self.corpora = None
        self.us_train_data = None

    def prepare_corpora(self):
        self.corpora = OntoAlignCorpora(
            self.src_ob,
            self.tgt_ob,
            self.train_map_ratio,
            self.val_map_ratio,
            self.test_map_ratio,
            self.sample_rate,
            self.io_soft_neg_rate,
            self.io_hard_neg_rate,
            self.depth_threshold,
            self.depth_strategy
        )
        self.us_train_data = self.corpora.unsupervised_data()
        print("Unsupervised fine_tuning data with following sizes:")
        print(f"\ttrain: {len(self.us_train_data['train'])}")
        print(f"\ttrain+: {len(self.us_train_data['train+'])}")
        print(f"\tval: {len(self.us_train_data['val'])}")
        print(f"\tval+: {len(self.us_train_data['val+'])}")

    def get_train_validation(self, with_idx: bool):
        if with_idx:
            return self.us_train_data["train+"], self.us_train_data["val+"]
        else:
            return self.us_train_data["train"], self.us_train_data["val"]
