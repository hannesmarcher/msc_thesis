from pathlib import Path
from typing import List

from ontology_preprocessing.clazz import Clazz


def generate_owl(filename_to_write: str, classes: List[Clazz], base_iri: str, template_path = None):
    if template_path is None:
        template_path = "./template.owl"

    print(f"Reading finished; writing results to {filename_to_write}")

    template = open(template_path, 'r')
    template_lines = template.readlines()

    lines = []

    for template_line in template_lines:
        if "--BASE--" in template_line:
            lines.append(template_line.replace("--BASE--", base_iri))
        elif "--CLASSES--" in template_line:
            for cso_class in classes:
                id = cso_class.idx.replace("<", "").replace(">", "")
                lines.append(f"\t<owl:Class rdf:about=\"{id}\">\n")
                for label in cso_class.labels:
                    label = label.split("\"@en")[0].replace("\"", "", 1)
                    lines.append(f"\t\t<rdfs:label xml:lang=\"en\">{label}</rdfs:label>\n")
                for subclass in cso_class.subClassOf:
                    subclass_id = subclass.replace("<", "").replace(">", "")
                    lines.append(f"\t\t<rdfs:subClassOf rdf:resource=\"{subclass_id}\"/>\n")
                lines.append("\t</owl:Class>\n")
        else:
            lines.append(template_line)

    Path(filename_to_write[::-1].split("/", 1)[1][::-1]).mkdir(parents=True, exist_ok=True)
    newfile = open(filename_to_write, 'w+')
    newfile.writelines(lines)
