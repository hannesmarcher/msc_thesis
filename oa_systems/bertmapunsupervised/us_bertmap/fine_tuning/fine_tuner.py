import os
from typing import List

import torch
from transformers import TrainingArguments, IntervalStrategy

from us_bertmap.fine_tuning.bert_trainer import BERTTrainer


class FineTuner():
    def __init__(
            self,
            task_directory: str,
            train: List[str],
            validation: List[str],
            pre_trained_bert_path: str,
            max_length: int,
            early_stop: bool,
            early_stop_patience: int,
            batch_size: int,
            num_epochs: int,
            warm_up_ratio: float
    ):
        self.task_directory = task_directory
        self.warm_up_ratio = warm_up_ratio
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.early_stop_patience = early_stop_patience
        self.early_stop = early_stop
        self.max_length = max_length
        self.pre_trained_bert_path = pre_trained_bert_path
        self.validation = validation
        self.train = train

    def start_fine_tuning(self):
        torch.cuda.empty_cache()
        bert_oa = BERTTrainer(
            self.pre_trained_bert_path,
            self.train,
            self.validation,
            max_length=self.max_length,
            early_stop=self.early_stop,
            early_stop_patience=self.early_stop_patience,
        )

        for file in os.listdir(self.task_directory + "/bert_output"):
            if file.startswith("checkpoint"):
                print("skip fine-tuning as checkpoints exist")
                return

        epoch_steps = len(bert_oa.tra) // self.batch_size  # total steps of an epoch
        if torch.cuda.device_count() > 0:
            epoch_steps = epoch_steps // torch.cuda.device_count()  # to deal with multi-gpus case
        # keep logging steps consisitent even for small batch size
        # report logging on every 0.02 epoch
        logging_steps = int(epoch_steps * 0.02 + 1) # add 1 to prevent 0 for small ontologies
        # eval on every 0.1 epoch
        eval_steps = 5 * logging_steps

        training_args = TrainingArguments(
            output_dir=f"{self.task_directory}/bert_output",  # to save the checkpoints from training
            # max_steps=eval_steps*4 + 1,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            warmup_ratio=self.warm_up_ratio,
            weight_decay=0.01,
            logging_steps=logging_steps,
            logging_dir=f"{self.task_directory}/bert_output/tb",
            eval_steps=eval_steps,
            evaluation_strategy=IntervalStrategy.STEPS,
            do_train=True,
            do_eval=True,
            save_steps=eval_steps,
            load_best_model_at_end=True,
            save_total_limit=1
        )

        bert_oa.train(training_args)
