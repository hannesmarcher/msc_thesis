import re

import numpy as np
import pandas as pd
from rdflib import Graph

# rdflib is very slow, therefore for  very large reference files a manual appraoch is favorable


def parse_reference_rdf_file_manually(filepath: str) -> pd.DataFrame:
    file = open(filepath, "r")
    lines = file.readlines()

    entities1 = []
    entities2 = []
    values = []
    for line in lines:
        line = line.strip()
        if line[0:8] == "<entity1":
            url = re.findall('<entity1 rdf:resource="(.*)"/>', line)[0]
            entities1.append(url)
        elif line[0:8] == "<entity2":
            url = re.findall('<entity2 rdf:resource="(.*)"/>', line)[0]
            entities2.append(url)
        elif line[0:8] == "<measure":
            measure = re.findall('<measure rdf:datatype="xsd:float">(.*)</measure>', line)[0]
            values.append(float(measure))

    return pd.DataFrame(data={
        "Entity1": entities1,
        "Entity2": entities2,
        "Value": values
    })


def parse_reference_rdf_file(filepath: str) -> pd.DataFrame:
    g = Graph()
    g.parse(f"file://{filepath}", format="application/rdf+xml")

    alignment_base_url = [t[1] for t in g.namespaces() if len(t[0]) == 0][0]

    all_maps = np.unique([
        [str(obj)] for (_, pred, obj) in g if
        str(pred) == f"{alignment_base_url}map"
    ])

    sources = []
    targets = []
    values = []
    for bnode_map in all_maps:
        result = [(pred, obj) for subj, pred, obj in g if str(subj) == bnode_map]
        entity1 = [str(obj) for (pred, obj) in result if
                   str(pred) == f"{alignment_base_url}entity1"][0]
        entity2 = [str(obj) for (pred, obj) in result if
                   str(pred) == f"{alignment_base_url}entity2"][0]
        value = [str(obj) for (pred, obj) in result if
                 str(pred) == f"{alignment_base_url}measure"][0]

        sources.append(entity1)
        targets.append(entity2)
        values.append(value)

    return pd.DataFrame(data={
        "Entity1": sources,
        "Entity2": targets,
        "Value": values
    })
