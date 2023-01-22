import os

import pandas as pd

from helpers.parse_reference_rdf_file import parse_reference_rdf_file

if __name__ == "__main__":
    for task_name in ["cpc2ccs", "cpc2cso"]:
        print(f"Running task {task_name}")

        if task_name == "cpc2ccs":
            references_file_path = f"../../oa_systems/logmap/{task_name}_full/logmap2_mappings.rdf"
        elif task_name == "cpc2cso":
            references_file_path = f"../../oa_systems/aml/{task_name}_full/references.rdf"
        else:
            raise Exception()

        partial_gold_standard_path = f"../../ontologies/sub_ontologies/{task_name}/references.rdf"
        sample_file_path = f"../../analysis_full_alignments/{task_name}_sample_annotated.tsv"

        df_generated_alignments = parse_reference_rdf_file(os.path.abspath(references_file_path)).drop("Value", axis=1)
        df_partial_gold_standard = parse_reference_rdf_file(os.path.abspath(partial_gold_standard_path))\
            .drop("Value", axis=1)
        df_sample = pd.read_csv(sample_file_path, sep="\t")

        m = len(df_generated_alignments)
        m_intersection_g = len(pd.merge(df_generated_alignments, df_partial_gold_standard, how="inner"))
        m_setdiff_g = len(pd.merge(df_generated_alignments, df_partial_gold_standard, indicator=True, how='outer') \
            .query('_merge=="left_only"') \
            .drop('_merge', axis=1))
        s = len(df_sample)
        s_v = len(df_sample[df_sample.is_correct == True])

        print(f"|M|={m}")
        print(f"|M intersection G|={m_intersection_g}")
        print(f"|M setdiff G|={m_setdiff_g}")
        print(f"|S|={s}")
        print(f"|S_v|={s_v}")

        precision = (m_intersection_g + (s_v / s) * m_setdiff_g) / m
        print(f"Precision~={precision}")
        print("---------------------------------------------")

        sample_recall_file_path = f"../../analysis_full_alignments/{task_name}_recall_sample_annotated.tsv"
        all_mappings_recall_file_path = f"../../analysis_full_alignments/{task_name}_recall_all_mappings.tsv"
        df_sample_recall = pd.read_csv(sample_recall_file_path, sep="\t")
        df_all_mappings_recall = pd.read_csv(all_mappings_recall_file_path, sep="\t")
        m_prime_setdiff_g = len(df_all_mappings_recall)
        s_prime = len(df_sample_recall)
        s_v_prime = len(df_sample_recall[df_sample_recall.is_correct == True])
        g = len(df_partial_gold_standard)

        print(f"|M' setdiff G|={m_prime_setdiff_g}")
        print(f"|S'|={s_prime}")
        print(f"|S'_v|={s_v_prime}")
        print(f"|G|={g}")

        recall = (m_intersection_g + (s_v / s) * m_setdiff_g) / (g + (s_v_prime / s_prime) * m_prime_setdiff_g)
        print(f"Recall~={recall}")
        print("---------------------------------------------")

        print(f"f1-score~={2 * precision * recall / (precision + recall)}")
        print("---------------------------------------------")

