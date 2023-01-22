import re
import urllib
from typing import List

import pandas as pd

from ground_truth.cso_cluster_finder import CSOClusterFinder


class CSOMissingSynonymDetector:

    @staticmethod
    def check_if_synonyms_are_missing(cso_filename: str, references_file_name: str) -> None:
        df_references = pd.read_csv(references_file_name, sep="\t")
        df_references.fillna("", inplace=True)

        lines = CSOClusterFinder.get_clusters(cso_filename)

        clusters: List[List[str]] = []
        for line in lines:
            clusters.append([urllib.parse.unquote(m.replace("_", " ")) for m in line])

        for cso_label in list(df_references.cso_label):
            labels = re.findall(";?\s*(.*?)\s*\(\d+\.?\d*\)", cso_label)
            for label in labels:
                label_existing_in_one_cluster = False
                for cluster in clusters:
                    if label in cluster:
                        label_existing_in_one_cluster = True
                        if any([l not in labels for l in cluster]):
                            print(f"WARNING: labels: {labels} do not contain at least one label from cluster: {cluster}")
                if not label_existing_in_one_cluster:
                    print(f"WARNING: label: {label} is not contained in any cluster and is therefore not existent!")
