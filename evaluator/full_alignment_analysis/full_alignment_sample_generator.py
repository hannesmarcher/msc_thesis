import os

import pandas as pd
from owlready2 import get_ontology

from helpers.id_to_label_parser import parse_tuples_to_first_label
from helpers.parse_reference_rdf_file import parse_reference_rdf_file

# Unfortunately the outcome of this script does not correspond to the samples in ../../analysis_full_alignments/
#   as the original files were generated when this script was not yet deterministic
if __name__ == "__main__":
    for task_name in ["cpc2ccs", "cpc2cso"]:
        if task_name == "cpc2ccs":
            references_file_path = f"../../oa_systems/logmap/{task_name}_full/logmap2_mappings.rdf"
            partial_gold_standard_path = f"../../ontologies/sub_ontologies/{task_name}/references.rdf"
        elif task_name == "cpc2cso":
            references_file_path = f"../../oa_systems/aml/{task_name}_full/references.rdf"
            partial_gold_standard_path = f"../../ontologies/sub_ontologies/{task_name}/references.rdf"
        else:
            raise Exception()
        cpc_file_path = f"../../ontologies/full_ontologies/{task_name}/source.owl"
        other_file_path = f"../../ontologies/full_ontologies/{task_name}/target.owl"

        df_generated_alignments = parse_reference_rdf_file(os.path.abspath(references_file_path))
        print(f"size of alignment: {len(df_generated_alignments)}")
        df_partial_gold_standard = parse_reference_rdf_file(os.path.abspath(partial_gold_standard_path))
        df_generated_alignments_without_gs = pd.merge(
            df_generated_alignments.drop("Value", axis=1),
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
        df = df.sample(min(100, len(data["source"])), random_state=0)
        df.sort_values(by="source_id", inplace=True)

        df.to_csv(f"../../analysis_full_alignments/{task_name}_sample.tsv", sep="\t", index=False)
