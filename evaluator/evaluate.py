import os
from pathlib import Path

import pandas as pd
from owlready2 import get_ontology

from helpers.id_to_label_parser import parse_tuples_to_first_label
from helpers.parse_reference_rdf_file import parse_reference_rdf_file


def evaluate(all_generated_alignment_files, task_name_plus_gs_type_indication, cpc_file_path, other_file_path, gold_standard_file_path):
    if not Path(gold_standard_file_path).exists():
        print(f"File {gold_standard_file_path} does not exist for task {task_name_plus_gs_type_indication}")
        return

    tp_map = dict()
    fp_map = dict()
    expected_not_predicted_map = dict()

    onto_cpc = get_ontology(cpc_file_path).load()
    onto_other = get_ontology(other_file_path).load()

    assert gold_standard_file_path is not None
    assert onto_cpc is not None
    assert onto_other is not None

    df_gold_standard = parse_reference_rdf_file(os.path.abspath(gold_standard_file_path))
    metrics = dict()
    metrics["precision"] = []
    metrics["recall"] = []
    metrics["f1"] = []
    metrics["#TP"] = []
    metrics["#FP"] = []
    metrics["#Gold_Standard"] = []
    metrics_index = []

    for matcher, generated_alignment_file_path in all_generated_alignment_files:
        metrics_index.append(matcher)
        if not Path(generated_alignment_file_path).exists():
            metrics["precision"].append("NA")
            metrics["recall"].append("NA")
            metrics["f1"].append("NA")
            metrics["#TP"].append("NA")
            metrics["#FP"].append("NA")
            metrics["#Gold_Standard"].append("NA")
            tp_map[matcher] = []
            fp_map[matcher] = []
            expected_not_predicted_map[matcher] = []
            continue
        df_generated_alignments = parse_reference_rdf_file(os.path.abspath(generated_alignment_file_path))

        expected_tuples = list(zip(df_gold_standard.Entity1, df_gold_standard.Entity2))
        predicted_tuples = list(zip(df_generated_alignments.Entity1, df_generated_alignments.Entity2))

        true_positives = [t for t in predicted_tuples if t in expected_tuples]
        false_positives = [t for t in predicted_tuples if t not in expected_tuples]
        expected_but_not_predicted = [t for t in expected_tuples if t not in predicted_tuples]

        precision = len(true_positives) / len(predicted_tuples) if len(predicted_tuples) > 0 else 0
        recall = len(true_positives) / len(expected_tuples)
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        print(f"{matcher} Precision: {precision}")
        print(f"{matcher} Recall: {recall}")
        print(f"{matcher} F1: {f1}")
        print(f"{matcher} #TP: {len(true_positives)}")
        print(f"{matcher} #FP: {len(false_positives)}")
        print(f"{matcher} #Gold_Standard: {len(expected_tuples)}")
        metrics["precision"].append(precision)
        metrics["recall"].append(recall)
        metrics["f1"].append(f1)
        metrics["#TP"].append(len(true_positives))
        metrics["#FP"].append(len(false_positives))
        metrics["#Gold_Standard"].append(len(expected_tuples))
        print("--------------------------------------------------------------------")

        tp_map[matcher] = true_positives
        fp_map[matcher] = false_positives
        expected_not_predicted_map[matcher] = expected_but_not_predicted

    pd.DataFrame(data=metrics, index=metrics_index).to_csv(f"./results/{task_name_plus_gs_type_indication}_metrics.tsv", sep="\t")

    if "cpc2ccs" not in task_name_plus_gs_type_indication and "cpc2cso" not in task_name_plus_gs_type_indication:
        return

    all_predicted_alignments = []
    correct_match_indication = []
    for _, tp_tuples in tp_map.items():
        all_predicted_alignments.extend([t for t in tp_tuples if t not in all_predicted_alignments])
        correct_match_indication.extend([True] * len(tp_tuples))
    correct_match_indication = correct_match_indication[0:len(all_predicted_alignments)]
    for _, fp_tuples in fp_map.items():
        all_predicted_alignments.extend([t for t in fp_tuples if t not in all_predicted_alignments])
        correct_match_indication.extend([False] * len(fp_tuples))
    correct_match_indication = correct_match_indication[0:len(all_predicted_alignments)]
    for _, expected_tuples in expected_not_predicted_map.items():
        all_predicted_alignments.extend([t for t in expected_tuples if t not in all_predicted_alignments])
        correct_match_indication.extend([True] * len(expected_tuples))
    correct_match_indication = correct_match_indication[0:len(all_predicted_alignments)]

    matcher_predicted_indication = dict()
    for matcher, _ in all_generated_alignment_files:
        matcher_predicted_indication[matcher] = [t in tp_map[matcher] or t in fp_map[matcher] for t in
                                                 all_predicted_alignments]

    data = dict()
    all_predicted_alignments_labels = parse_tuples_to_first_label(all_predicted_alignments, onto_cpc, onto_other)
    data["source"] = [t[0] for t in all_predicted_alignments_labels]
    data["target"] = [t[1] for t in all_predicted_alignments_labels]
    data["is_correct"] = [tp for tp in correct_match_indication]
    for matcher, prediction_indication in matcher_predicted_indication.items():
        data[matcher] = prediction_indication

    pd.DataFrame(data=data).to_csv(f"./results/{task_name_plus_gs_type_indication}_tp_fp_analysis.tsv", sep="\t")


if __name__ == "__main__":

    # To distinguish between docker execution and python execution
    if os.getcwd()[-9:] == "evaluator":
        os.chdir("../")

    Path("./results").mkdir(exist_ok=True)

    tasks = ["cpc2ccs", "cpc2cso", "anatomy"]

    for task_name in tasks:
        all_generated_alignment_files = [
            ("logmap", f"./oa_systems/logmap/{task_name}/references.rdf"),
            ("logmap_exp", f"./oa_systems/logmap/{task_name}_experimental/references.rdf"),
            ("logmap-lt", f"./oa_systems/logmap_lite/{task_name}/references.rdf"),
            ("aml", f"./oa_systems/aml/{task_name}/references.rdf"),
            ("sanom", f"./oa_systems/sanom/docker/{task_name}/references.rdf"),
            ("sanom_wordnet", f"./oa_systems/sanom/docker/{task_name}_wordnet/references.rdf"),
            ("ontoconnect", f"./oa_systems/ontoconnect/{task_name}/references.rdf"),
            ("logmap-ml_owl2vec_star_label", f"./oa_systems/logmapml/docker/{task_name}_owl2vec_star_label/references.rdf"),
            ("logmap-ml_owl2vec_star_path", f"./oa_systems/logmapml/docker/{task_name}_owl2vec_star_path/references.rdf"),
            ("logmap-ml_word2vec_label", f"./oa_systems/logmapml/docker/{task_name}_word2vec_label/references.rdf"),
            ("logmap-ml_word2vec_path", f"./oa_systems/logmapml/docker/{task_name}_word2vec_path/references.rdf"),
            ("bertmap-us_200", f"./oa_systems/bertmapunsupervised/docker/{task_name}/reference.200.rdf"),
            ("bertmap-us_25", f"./oa_systems/bertmapunsupervised/docker/{task_name}/reference.25.rdf"),
            ("lxlhmeta", f"./oa_systems/meta_matcher/docker/{task_name}/references.rdf"),
            ("ljlevolutionary", f"./oa_systems/evolutionary_algorithm/docker/{task_name}/references.rdf"),
            ("baseline", f"./oa_systems/baseline/docker/{task_name}/references.rdf"),
        ]
        cpc_file_path = f"./ontologies/sub_ontologies/{task_name}/source.owl"
        other_file_path = f"./ontologies/sub_ontologies/{task_name}/target.owl"
        gold_standard_file_path_easy = f"./ontologies/sub_ontologies/{task_name}/references.easy.rdf"
        gold_standard_file_path = f"./ontologies/sub_ontologies/{task_name}/references.rdf"
        evaluate(all_generated_alignment_files, task_name + "_easy", cpc_file_path, other_file_path, gold_standard_file_path_easy)
        evaluate(all_generated_alignment_files, task_name + "_normal", cpc_file_path, other_file_path, gold_standard_file_path)

