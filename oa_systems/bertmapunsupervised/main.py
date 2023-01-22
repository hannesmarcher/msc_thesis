import argparse
import json
from pathlib import Path

from us_bertmap.extension.mappings_extension import MappingsExtension
from us_bertmap.fine_tuning.fine_tuner import FineTuner
from us_bertmap.prediction.compute_mappings import ComputeMappings
from us_bertmap.preprocessing.corpus_loader import CorpusLoader
from us_bertmap.preprocessing.onto_box_loader import OntoBoxLoader
from us_bertmap.repair.mapping_repair import MappingRepair
from us_bertmap.utils.helpers import banner
from us_bertmap.utils.helpers import set_seed
from us_bertmap.utils.rdf_creation_util import generate_all_rdf_files

if __name__ == "__main__":
    set_seed(0)

    parser = argparse.ArgumentParser(description="run bertmap system")
    parser.add_argument("-c", "--config", type=str, help="directory containing config.json file", required=True)
    parser.add_argument("-i", "--input", type=str, help="directory containing source.owl and target.owl files", required=True)
    parser.add_argument("-o", "--output", type=str, help="directory where all the output files should go", required=True)
    args = parser.parse_args()


    banner("load configurations", sym="#")
    config_dir = args.config
    input_dir = args.input
    output_dir = args.output

    configuration_path = f"{config_dir}/config.json"
    print("configuration-file: ")
    with open(configuration_path, "r") as f:
        config_json = json.load(f)
    for stage, stage_config in config_json.items():
        print(f"{stage} params:")
        for param, value in stage_config.items():
            print(f"\t{param}: {value}")

    # Preparation of data
    banner("prepare onto data", sym="#")
    data_params = config_json["data"]
    bert_params = config_json["bert"]

    onto_loader = OntoBoxLoader(
        output_dir,
        f"{input_dir}/source.owl",
        f"{input_dir}/target.owl",
        data_params["src_onto"],
        data_params["tgt_onto"],
        bert_params["tokenizer_path"],
        data_params["properties"]
    )
    onto_loader.prepare_data()

    # Construction of train & validation data
    banner("Construct Corpora", sym="#")
    corpora_params = config_json["corpora"]
    corpus_loader = CorpusLoader(
        src_ob=onto_loader.src_onto_box,
        tgt_ob=onto_loader.tgt_onto_box,
        sample_rate=corpora_params["sample_rate"],
        train_map_ratio=corpora_params["train_map_ratio"],
        val_map_ratio=corpora_params["val_map_ratio"],
        test_map_ratio=corpora_params["test_map_ratio"],
        io_soft_neg_rate=corpora_params["io_soft_neg_rate"],
        io_hard_neg_rate=corpora_params["io_hard_neg_rate"],
        depth_threshold=corpora_params["depth_threshold"],
        depth_strategy=corpora_params["depth_strategy"],
    )
    corpus_loader.prepare_corpora()

    # Fine-tuning of BERT
    banner("Start fine-tuning", sym="#")
    bert_output_path = f"{output_dir}/bert_output"
    Path(bert_output_path).mkdir(parents=True, exist_ok=True)
    fine_tune_params = config_json["fine-tune"]
    train, val = corpus_loader.get_train_validation(fine_tune_params["include_ids"])
    tuner = FineTuner(
        output_dir,
        train,
        val,
        bert_params["pretrained_path"],
        fine_tune_params["max_length"],
        fine_tune_params["early_stop"],
        fine_tune_params["early_stop_patience"],
        fine_tune_params["batch_size"],
        fine_tune_params["num_epochs"],
        fine_tune_params["warm_up_ratio"]
    )
    tuner.start_fine_tuning()

    # Creating the alignment
    banner("Start prediction", sym="#")
    mapping_params = config_json["map"]
    mappings_computer = ComputeMappings(
        bert_output_path,
        mapping_params["candidate_limits"],
        mapping_params["nbest"],
        mapping_params["string_match"],
        mapping_params["strategy"],
        bert_params["tokenizer_path"],
        fine_tune_params["max_length"]
    )
    mappings_computer.compute_map(onto_loader.src_onto_box, onto_loader.tgt_onto_box)

    # Mapping extension
    banner("Start extension", sym="#")
    extension_params = config_json["extension"]
    mapping_extension = MappingsExtension(
        bert_output_path,
        extension_params["threshold"],
        bert_params["tokenizer_path"],
        fine_tune_params["max_length"],
        mapping_params["string_match"],
        extension_params["max_iter"]
    )
    mapping_extension.extend_maps(onto_loader.src_onto_box, onto_loader.tgt_onto_box)

    # Mapping repair
    banner("Start repair", sym="#")
    repair_params = config_json["repair"]
    mapping_repair = MappingRepair(
        output_dir + "/src.onto",
        output_dir + "/tgt.onto",
        onto_loader.src_onto_box,
        onto_loader.tgt_onto_box,
        bert_output_path,
        "./us_bertmap/logmap/logmap-matcher-4.0.jar",
        repair_params["threshold"]
    )
    mapping_repair.repair_maps()

    banner("Generating rdf files", sym="#")
    generate_all_rdf_files(output_dir + "/bert_output", output_dir)
