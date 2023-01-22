import argparse
import os

from ground_truth.extract_matching_specific_references_ccs import CCSSpecificGroundTruthExtractor
from ground_truth.extract_matching_specific_references_cso import CSOSpecificGroundTruthExtractor
from ontology_preprocessing.ccs_preprocessor import CCSPreprocessor
from ontology_preprocessing.cpc_preprocessor import CPCPreprocessor
from ontology_preprocessing.cso_preprocessor import CSOPreprocessor


def prepare_ccs_data(args):
    print("Preprocessing CCS...", flush=True)
    ccs_filename = f"{args.resources}/acm_ccs2012-1626988337597.xml"
    filename_to_write = f"{args.full_ontologies}/cpc2ccs/target.owl"
    CCSPreprocessor.preprocess_ccs(
        ccs_filename,
        filename_to_write,
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    print(f"Writing full preprocessed CCS to {filename_to_write}")
    filename_to_write = f"{args.sub_ontologies}/cpc2ccs/target.owl"
    CCSPreprocessor.preprocess_ccs(
        ccs_filename,
        filename_to_write,
        categories_to_consider=["10011007"], # 10011007 = ID for "Software and its engineering"
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    print(f"Writing subset of CCS to {filename_to_write}")


def prepare_cso_data(args):
    cso_filename = f"{args.resources}/CSO.3.3.owl"
    print("Preprocessing CSO...")
    filename_to_write = f"{args.full_ontologies}/cpc2cso/target.owl"
    CSOPreprocessor.preprocess_cso(
        cso_filename,
        filename_to_write,
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    print(f"Writing full preprocessed CSO to {filename_to_write}")
    filename_to_write = f"{args.sub_ontologies}/cpc2cso/target.owl"
    categories_to_consider = [
        "https://cso.kmi.open.ac.uk/topics/computer_programming",
        "https://cso.kmi.open.ac.uk/topics/software",
        "https://cso.kmi.open.ac.uk/topics/software_engineering"]
    CSOPreprocessor.preprocess_cso(
        cso_filename,
        filename_to_write,
        categories_to_consider=categories_to_consider,
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    print(f"Writing subset of CSO to {filename_to_write}")


def prepare_cpc_data(args):
    print("Preprocessing CPC...")
    nt_filename = f"{args.resources}/cpc.nt"
    filename_to_write = f"{args.full_ontologies}/cpc2ccs/source.owl"
    filename_to_write2 = f"{args.full_ontologies}/cpc2cso/source.owl"
    CPCPreprocessor.preprocess_cpc_full(
        nt_filename,
        filename_to_write,
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    os.system(f"cp {filename_to_write} {filename_to_write2}")
    print(f"Writing full preprocessed CPC to {filename_to_write}")
    print(f"Writing full preprocessed CPC to {filename_to_write2}")

    ontology_file = filename_to_write
    filename_to_write = f"{args.sub_ontologies}/cpc2ccs/source.owl"
    filename_to_write2 = f"{args.sub_ontologies}/cpc2cso/source.owl"
    se_terms_kotti_et_al_2022 = f"{args.resources}/se-cpc.tsv"
    CPCPreprocessor.preprocess_cpc_sub(
        ontology_file,
        se_terms_kotti_et_al_2022,
        filename_to_write,
        path_to_owl_template="./ontology_preprocessing/template.owl"
    )
    os.system(f"cp {filename_to_write} {filename_to_write2}")
    print(f"Writing subset of CPC to {filename_to_write}")
    print(f"Writing subset of CPC to {filename_to_write2}")


def generate_ccs_gt(args):
    print("Generating CCS Ground Truth...")
    sub_ontology_file_path = f"{args.sub_ontologies}/cpc2ccs/target.owl"
    references_file_path = f"{args.resources}/ground_truth.tsv"
    tsv_file_path_to_write = f"{args.sub_ontologies}/cpc2ccs/references.tsv"
    rdf_file_path_to_write = f"{args.sub_ontologies}/cpc2ccs/references.rdf"
    tsv_file_path_to_write_easy = f"{args.sub_ontologies}/cpc2ccs/references.easy.tsv"
    rdf_file_path_to_write_easy = f"{args.sub_ontologies}/cpc2ccs/references.easy.rdf"
    CCSSpecificGroundTruthExtractor.generate_references(
        sub_ontology_file_path,
        references_file_path,
        tsv_file_path_to_write,
        rdf_file_path_to_write,
        tsv_file_path_to_write_easy,
        rdf_file_path_to_write_easy
    )


def generate_cso_gt(args):
    print("Generating CSO Ground Truth...")
    sub_ontology_file_path = f"{args.sub_ontologies}/cpc2cso/target.owl"
    references_file_path = f"{args.resources}/ground_truth.tsv"
    tsv_file_path_to_write = f"{args.sub_ontologies}/cpc2cso/references.tsv"
    rdf_file_path_to_write = f"{args.sub_ontologies}/cpc2cso/references.rdf"
    tsv_file_path_to_write_easy = f"{args.sub_ontologies}/cpc2cso/references.easy.tsv"
    rdf_file_path_to_write_easy = f"{args.sub_ontologies}/cpc2cso/references.easy.rdf"
    CSOSpecificGroundTruthExtractor.generate_references(
        sub_ontology_file_path,
        references_file_path,
        tsv_file_path_to_write,
        rdf_file_path_to_write,
        tsv_file_path_to_write_easy,
        rdf_file_path_to_write_easy
    )


if __name__ == "__main__":
    print("Start preprocessing...")
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--resources", type=str, required=True)
    parser.add_argument("-f", "--full_ontologies", type=str, required=True)
    parser.add_argument("-s", "--sub_ontologies", type=str, required=True)
    args = parser.parse_args()

    prepare_ccs_data(args)
    prepare_cso_data(args)
    prepare_cpc_data(args)
    generate_ccs_gt(args)
    generate_cso_gt(args)
