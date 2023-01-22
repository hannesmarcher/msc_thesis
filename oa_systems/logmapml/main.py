import argparse
import json
import os.path
import subprocess
from pathlib import Path
from shutil import copy2

from src.name_path import extract_names_and_paths
from src.ontology_stats_calculator import get_path_size_max_token_length
from src.predict_candidates import start_predictions
from src.rdf_file_generator import generate_rdf_file
from src.sample import sample
from src.train_valid import train_valid


if __name__ == "__main__":

    # Initializing:
    parser = argparse.ArgumentParser(description="run bertmap system")
    parser.add_argument("-c", "--config", type=str, help="directory containing config.json file", required=True)
    parser.add_argument("-i", "--input", type=str, help="directory containing source.owl and target.owl files",
                        required=True)
    parser.add_argument("-o", "--output", type=str, help="directory where all the output files should go",
                        required=True)
    args = parser.parse_args()


    source_onto_path = f"{args.input}/source.owl"
    target_onto_path = f"{args.input}/target.owl"
    configuration_path = f"{args.config}/config.json"
    print("Found Configuration:")
    with open(configuration_path, "r") as f:
        config_json = json.load(f)
    for stage, stage_config in config_json.items():
        print(f"\t{stage} value: {stage_config}")

    Path(args.output).mkdir(parents=True, exist_ok=True)
    copy2(configuration_path, f"{args.output}/used_config.json")
    copy2(source_onto_path, f"{args.output}/source.owl")
    copy2(target_onto_path, f"{args.output}/target.owl")

    # Extracting names and paths:
    source_onto_names = f"{args.output}/source_class_name.json"
    source_onto_paths = f"{args.output}/source_all_paths.txt"
    target_onto_names = f"{args.output}/target_class_name.json"
    target_onto_paths = f"{args.output}/target_all_paths.txt"
    extract_names_and_paths(source_onto_path, name_file=source_onto_names, path_file=source_onto_paths)
    extract_names_and_paths(target_onto_path, name_file=target_onto_names, path_file=target_onto_paths)

    # Generating LogMap's anchor mappings and overestimations
    print("Generating anchor mappings")
    logmap_jar_path = os.path.abspath("./src/logmap_directory/logmap-matcher-4.0.jar")
    logmap_output_path = os.path.abspath(f"{args.output}/logmap_output/") + "/"
    Path(logmap_output_path).mkdir(parents=True, exist_ok=True)
    logmap_command = f"java -jar {logmap_jar_path} MATCHER file:{os.path.abspath(source_onto_path)} file:{os.path.abspath(target_onto_path)} {logmap_output_path} true"
    logmap_process = subprocess.Popen(logmap_command.split(" "), cwd="./src/logmap_directory")
    logmap_process.communicate()

    # Sampling
    print("Sampling")
    train_file_path = f"{args.output}/mappings_train.txt"
    validation_file_path = f"{args.output}/mappings_valid.txt"
    sample(argparse.Namespace(
        anchor_mapping_file=logmap_output_path + "logmap_anchors.txt",
        train_file=train_file_path,
        valid_file=validation_file_path,
        left_path_file=source_onto_paths,
        right_path_file=target_onto_paths,
        left_class_name_file=source_onto_names,
        right_class_name_file=target_onto_names,
        keep_uri="no",
        anchor_branch_conflict="yes",
        generate_negative_sample="yes",
        anchor_GS="no",
        GS_file="",
        train_rate=1.0,
        sample_duplicate=2,

    ))

    # Train, Valid, and Predict
    print("Starting triain & validation phase")
    embedding_type = config_json["embedding"]
    assert embedding_type == "word2vec" or embedding_type == "owl2vec_star"
    word2vec_dir = f"./word2vec/word2vec_gensim" if embedding_type == "word2vec" else f"./owl2vec_star/ontology.embeddings"
    if not Path(word2vec_dir).exists():
        print(f"ERROR: please provide an embeddings file, named: {word2vec_dir}")

    assert Path(word2vec_dir).exists()

    print("\tComputing max path size and max token length")
    path_size_source, max_token_length_source, path_size_target, max_token_length_target = get_path_size_max_token_length(source_onto_path, target_onto_path)
    print(f"\tFound max path size of {path_size_source} in source ontology")
    print(f"\tFound max path size of {path_size_target} in target ontology")
    print(f"\tFound max token length of {max_token_length_source} in source ontology")
    print(f"\tFound max token length of {max_token_length_target} in target ontology")

    path_type = config_json["path_type"]
    assert path_type == "label" or path_type == "path"
    nn_base_dir = f"{args.output}/model_label"
    # Note if sample size is too small, the returned threshold is not useful
    #   Thus set it to 0.8 (see below)
    best_nn_type, best_encoder_type, _ = train_valid(argparse.Namespace(
        train_path_file=train_file_path,
        valid_path_file=validation_file_path,
        class_word_size=max(max_token_length_source, max_token_length_target),
        left_path_size=path_size_source,
        right_path_size=path_size_target,
        left_w2v_dir=word2vec_dir,
        right_w2v_dir=word2vec_dir,
        vec_type="word",
        path_type=path_type,
        nn_base_dir=nn_base_dir,
        rnn_hidden_size=200,
        rnn_attention_size=50,
        mlp_hidden_size=200,
        num_epochs=14,
        batch_size=8,
        evaluate_every=100
    ))

    # Prediction
    print("Starting with predictions")
    start_predictions(argparse.Namespace(
        left_path_file=source_onto_paths,
        right_path_file=target_onto_paths,
        left_class_name_file=source_onto_names,
        right_class_name_file=target_onto_names,
        closest_anns_file="",
        candidate_file=f"{logmap_output_path}logmap_overestimation.txt",
        prediction_out_file=f"{args.output}/predict_score.txt",
        class_word_size=max(max_token_length_source, max_token_length_target),
        left_path_size=path_size_source,
        right_path_size=path_size_target,
        left_w2v_dir=word2vec_dir,
        right_w2v_dir=word2vec_dir,
        path_type=path_type,
        vec_type="word",
        keep_uri="no",
        encoder_type=best_encoder_type,
        nn_dir=nn_base_dir,
        nn_type=best_nn_type
    ))

    # Generating rdf alignments file
    generate_rdf_file(f"{args.output}/predict_score.txt", f"{args.output}/references.rdf", 0.8)



