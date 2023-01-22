from typing import Tuple

import pandas as pd


def create_rdf(tsv_file_path_to_read: str, rdf_file_path_to_write: str, abbrv_iri_tuple: Tuple[str, str]):
    cpc_abbrv_iri_tuple = ('cpc', 'http://data.epo.org/linked-data/def/cpc/')
    df = pd.read_csv(tsv_file_path_to_read, sep="\t")

    lines = []

    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<rdf:RDF xmlns="http://knowledgeweb.semanticweb.org/heterogeneity/alignment#"')
    lines.append('	 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" ')
    lines.append('	 xmlns:xsd="http://www.w3.org/2001/XMLSchema#">')
    lines.append('')
    lines.append('<Alignment>')
    lines.append('<xml>yes</xml>')
    lines.append('<level>0</level>')
    lines.append('<type>??</type>')

    for index, row in df.iterrows():
        entity1 = row.Entity1.replace(cpc_abbrv_iri_tuple[0] + ":", cpc_abbrv_iri_tuple[1])
        entity2 = row.Entity2.replace(abbrv_iri_tuple[0] + ":", abbrv_iri_tuple[1])
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

    newfile = open(rdf_file_path_to_write, 'w')
    newfile.writelines(lines)