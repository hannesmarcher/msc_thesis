"""
This file is C&P from scripts/ folder
"""
import os
import re
from shutil import copy2


def generate_all_rdf_files(directory_to_maps: str, directory_to_write_final_alignments: str):
    for file in os.listdir(directory_to_maps):
        if file.startswith("map"):
            current_map_directory = directory_to_maps + "/" + file
            candidate_limit = re.findall("map.(\d+)", file)[0]
            copy2(current_map_directory + "/repaired/mappings_repaired_with_LogMap.rdf",
                  directory_to_write_final_alignments + f"/reference.{candidate_limit}.rdf")
            # _generate_rdf_file(path + "/combined." + candidate_limit + ".tsv", path + "/reference.rdf")


"""
def _generate_rdf_file(path_to_tsv_file: str, rdf_file_name: str):
    alias = [
        ('cpc', 'http://cpc.se.owl#'),
        ('cso', 'https://cso.kmi.open.ac.uk/topics/')
    ]
    df = pd.read_csv(path_to_tsv_file, sep="\t")

    lines = []

    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<rdf:RDF xmlns="http://knowledgeweb.semanticweb.org/heterogeneity/alignment"')
    lines.append('	 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" ')
    lines.append('	 xmlns:xsd="http://www.w3.org/2001/XMLSchema#">')
    lines.append('')
    lines.append('<Alignment>')
    lines.append('<xml>yes</xml>')
    lines.append('<level>0</level>')
    lines.append('<type>??</type>')

    for index, row in df.iterrows():
        entity1 = row.Entity1.replace(alias[0][0] + ":", alias[0][1])
        entity2 = row.Entity2.replace(alias[1][0] + ":", alias[1][1])
        lines.append('<map>')
        lines.append('	<Cell>')
        lines.append(f'\t\t<entity1 rdf:resource="' + entity1 + '"/>')
        lines.append(f'\t\t<entity2 rdf:resource="' + entity2 + '"/>')
        lines.append(f'\t\t<measure rdf:datatype="xsd:float">' + str(row.Value) + '</measure>')
        lines.append('		<relation>=</relation>')
        lines.append('	</Cell>')
        lines.append('</map>')

    lines.append('</Alignment>')
    lines.append('</rdf:RDF>')

    lines = list(map(lambda x: x + "\n", lines))

    newfile = open(rdf_file_name, 'w')
    newfile.writelines(lines)
"""
