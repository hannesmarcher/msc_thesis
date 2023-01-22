import os

import pandas as pd
from owlready2 import get_ontology

from helpers.id_to_label_parser import parse_tuples_to_first_label
from helpers.parse_reference_rdf_file import parse_reference_rdf_file, parse_reference_rdf_file_manually

if __name__ == "__main__":
    for task_name in ["cpc2ccs", "cpc2cso"]:
        all_references = [
            f"../../oa_systems/logmap/{task_name}_full/logmap2_mappings.rdf",
            f"../../oa_systems/logmap_lite/{task_name}_full/logmap-lite-mappings.rdf",
            f"../../oa_systems/logmap/{task_name}_experimental_full/logmap2_mappings.rdf",
            f"../../oa_systems/aml/{task_name}_full/references.rdf",
            f"../../oa_systems/baseline/docker/{task_name}_full/references.rdf"
        ]
        # if task_name == "cpc2ccs":
        #     all_references.append( f"../../oa_systems/meta_matcher/docker/{task_name}_full/references.rdf")

        partial_gold_standard_path = f"../../ontologies/sub_ontologies/{task_name}/references.rdf"

        cpc_file_path = f"../../ontologies/full_ontologies/{task_name}/source.owl"
        other_file_path = f"../../ontologies/full_ontologies/{task_name}/target.owl"

        df_references = pd.DataFrame(columns=["Entity1", "Entity2"])
        for reference in all_references:
            print(f"Parse {reference}")
            if "meta_matcher" in reference:
                df_temp = parse_reference_rdf_file_manually(os.path.abspath(reference)).drop("Value", axis=1)
            else:
                df_temp = parse_reference_rdf_file(os.path.abspath(reference)).drop("Value", axis=1)
            df_references = pd.concat((df_references, df_temp))

        df_references.drop_duplicates(inplace=True)

        print(f"size of union: {len(df_references)}")
        df_partial_gold_standard = parse_reference_rdf_file(os.path.abspath(partial_gold_standard_path))
        df_generated_alignments_without_gs = pd.merge(
            df_references,
            df_partial_gold_standard.drop("Value", axis=1), indicator=True, how='outer').query(
            '_merge=="left_only"').drop('_merge', axis=1)

        onto_cpc = get_ontology(cpc_file_path).load()
        onto_other = get_ontology(other_file_path).load()

        predicted_tuples = list(
            zip(df_generated_alignments_without_gs.Entity1, df_generated_alignments_without_gs.Entity2))
        all_predicted_alignments_labels = parse_tuples_to_first_label(predicted_tuples, onto_cpc, onto_other)
        data = dict()
        data["source"] = [t[0] for t in all_predicted_alignments_labels]
        data["target"] = [t[1] for t in all_predicted_alignments_labels]
        data["source_id"] = [t[0][::-1].split("/")[0][::-1] for t in predicted_tuples]
        data["source_id"] = [(s[:4] + " " + s[4:]).replace("-", "/") for s in data["source_id"]]
        data["target_id"] = [t[1][::-1].split("/")[0][::-1] for t in predicted_tuples]
        df = pd.DataFrame(data=data).sort_values(by="source_id")
        df.to_csv(f"../../analysis_full_alignments/{task_name}_recall_all_mappings.tsv", sep="\t", index=False)
        df = df.sample(min(50, len(data["source"])), random_state=0)
        df.sort_values(by="source_id", inplace=True)

        df.to_csv(f"../../analysis_full_alignments/{task_name}_recall_sample.tsv", sep="\t", index=False)
