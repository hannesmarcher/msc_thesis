import re
import string

import pandas as pd
from owlready2 import get_ontology, IndividualValueList, entity

from ground_truth.create_rdf_file_from_tsv_reference_file import create_rdf


class CCSSpecificGroundTruthExtractor:

    @staticmethod
    def generate_references(
            sub_ontology_file_path: str,
            references_file_path: str,
            tsv_file_path_to_write: str,
            rdf_file_path_to_write: str,
            tsv_file_path_to_write_easy: str,
            rdf_file_path_to_write_easy: str
    ):
        # Extract id to label map
        onto = get_ontology(f"file://{sub_ontology_file_path}").load()
        label_to_id_map = dict()
        all_ids = []
        for clazz in onto.classes():
            assert type(clazz) is entity.ThingClass
            values = getattr(clazz, "label")
            assert type(values) is IndividualValueList
            idx = str(clazz.iri).split("/")[-1]
            if values[0] not in label_to_id_map:
                label_to_id_map[values[0]] = []
            label_to_id_map[values[0]].append(idx)
            all_ids.append(idx)


        df = pd.read_csv(references_file_path, sep="\t")
        df.fillna("", inplace=True)

        cpc_classification_symbols = [symbol.replace("/", "-") for symbol in list(df.cpc_classification_symbol)]
        other_ontology_ids = list(df["ccs_label"])

        tuples: [(string, string)] = list(zip(cpc_classification_symbols, other_ontology_ids))

        ccs_labels = []
        all_scores = []
        cpc_classification_symbols_extended = []
        for tuple in tuples:
            if len(tuple[1]) == 0:
                cpc_classification_symbols.remove(str(tuple[0]))
                continue
            matching_ids = re.findall(";?\s*(.*?)\s*\(\d+\.?\d*\)", tuple[1])
            similarity_scores = [float(match) for match in re.findall("\((\d+\.?\d*)\)", tuple[1])]
            if len(matching_ids) != len(similarity_scores):
                print("WARNING: length of matching ids is not the same as length of similarity scores")
            cpc_classification_symbols_extended.extend([tuple[0]] * len(matching_ids))
            ccs_labels.extend(matching_ids)
            all_scores.extend(similarity_scores)

        ccs_ids = []
        for label in ccs_labels:
            # Check if label is already an ID:
            if label in all_ids:
                ccs_ids.append(label)
                continue

            if label not in label_to_id_map:
                print(f"ERROR: the label {label} does not exist in this CCS sub-ontology!")
            elif len(label_to_id_map[label]) > 1:
                print(f"ERROR: the label {label} exists twice in this CCS sub-ontology, thus it is ambiguous!")
                print(f"\tPlease use ID instead of label in {references_file_path}")
                print(f"\tThe IDs are: {label_to_id_map[label]}")
            assert len(label_to_id_map[label]) == 1

            ccs_ids.append(label_to_id_map[label][0])

        lines = []
        lines_easy = []
        header = "Entity1\tEntity2\tValue" + "\n"
        print(header, end="")
        lines.append(header)
        lines_easy.append(header)
        for triple in list(zip(cpc_classification_symbols_extended, ccs_ids, all_scores)):
            current_line = "cpc:" + triple[0] + "\t"
            current_line += f"ccs:" + triple[1] + "\t" + str(triple[2]) + "\n"
            lines.append(current_line)
            if triple[2] >= 0.9:
                lines_easy.append(current_line)

        newfile = open(tsv_file_path_to_write, 'w')
        newfile.writelines(lines)
        newfile.flush()

        newfile = open(tsv_file_path_to_write_easy, 'w')
        newfile.writelines(lines_easy)
        newfile.flush()

        # Creation of RDF file

        print("Start creation of RDF files")
        create_rdf(tsv_file_path_to_write, rdf_file_path_to_write, ('ccs', 'https://dl.acm.org/ccs/topics/'))
        create_rdf(tsv_file_path_to_write_easy, rdf_file_path_to_write_easy, ('ccs', 'https://dl.acm.org/ccs/topics/'))