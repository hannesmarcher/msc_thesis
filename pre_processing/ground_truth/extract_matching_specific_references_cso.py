import re
import string
import urllib.parse

import pandas as pd
from owlready2 import get_ontology

from ground_truth.create_rdf_file_from_tsv_reference_file import create_rdf
from ground_truth.cso_missing_synonym_detector import CSOMissingSynonymDetector


class CSOSpecificGroundTruthExtractor:

    @staticmethod
    def generate_references(
            sub_ontology_file_path: str,
            references_file_path: str,
            tsv_file_path_to_write: str,
            rdf_file_path_to_write: str,
            tsv_file_path_to_write_easy: str,
            rdf_file_path_to_write_easy: str
    ):
        CSOMissingSynonymDetector.check_if_synonyms_are_missing(sub_ontology_file_path, references_file_path)

        df = pd.read_csv(references_file_path, sep="\t")
        df.fillna("", inplace=True)

        cpc_classification_symbols = [symbol.replace("/", "-") for symbol in list(df.cpc_classification_symbol)]
        other_ontology_ids = list(df["cso_label"])

        tuples: [(string, string)] = list(zip(cpc_classification_symbols, other_ontology_ids))

        lines = []
        lines_easy = []
        header = "Entity1\tEntity2\tValue" + "\n"
        print(header, end="")
        lines.append(header)
        lines_easy.append(header)

        all_ids = []
        for tuple in tuples:
            if len(tuple[1]) == 0:
                continue
            matching_ids = re.findall(";?\s*(.*?)\s*\(\d+\.?\d*\)", tuple[1])
            matching_ids = [urllib.parse.quote(matching_id.replace(" ", "_")) for matching_id in matching_ids]
            all_ids.extend(matching_ids)
            similarity_scores = [float(match) for match in re.findall("\((\d+\.?\d*)\)", tuple[1])]
            if len(matching_ids) != len(similarity_scores):
                print("WARNING: length of matching ids is not the same as length of similarity scores")
            matching_ids_similarity_scores_tuples = list(zip(matching_ids, similarity_scores))
            for matching_id, similarity_score in matching_ids_similarity_scores_tuples:
                current_line = "cpc:" + tuple[0] + "\t"
                current_line += "cso:" + matching_id + "\t" + str(similarity_score) + "\n"
                print(current_line, end="")
                lines.append(current_line)
                if similarity_score >= 0.9:
                    lines_easy.append(current_line)

        # Verify that each id also appears in the sub-ontology
        onto = get_ontology(f"file://{sub_ontology_file_path}").load()
        for clazz in onto.classes():
            idx = str(clazz.iri).split("/")[-1]
            while idx in all_ids:
                all_ids.remove(idx)
            if len(all_ids) == 0:
                break

        for invalid_id in all_ids:
            print(f"ERROR the id {invalid_id} does not exist in CSO sub-ontology")
        assert len(all_ids) == 0

        newfile = open(tsv_file_path_to_write, 'w')
        newfile.writelines(lines)
        newfile.flush()

        newfile = open(tsv_file_path_to_write_easy, 'w')
        newfile.writelines(lines_easy)
        newfile.flush()

        # Creation of RDF file

        print("Start creation of RDF files")
        create_rdf(tsv_file_path_to_write, rdf_file_path_to_write, ('cso', 'https://cso.kmi.open.ac.uk/topics/'))
        create_rdf(tsv_file_path_to_write_easy, rdf_file_path_to_write_easy, ('cso', 'https://cso.kmi.open.ac.uk/topics/'))