def generate_rdf_file(prediction_scores_txt_path: str, rdf_file_path: str, threshold: float):
    prediction_scores_lines = open(prediction_scores_txt_path, 'r').readlines()

    def generate_map_string(entity1, entity2, similarity_score):
        result = "<map>\n"
        result = result + "\t<Cell>\n"
        result = result + f'\t\t<entity1 rdf:resource="{entity1}"/>\n'
        result = result + f'\t\t<entity2 rdf:resource="{entity2}"/>\n'
        result = result + f'\t\t<measure rdf:datatype="xsd:float">{similarity_score}</measure>\n'
        result = result + "\t\t<relation>=</relation>\n"
        result = result + "\t</Cell>\n"
        result = result + "</map>\n"

        return result

    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>\n')
    lines.append('<rdf:RDF xmlns="http://knowledgeweb.semanticweb.org/heterogeneity/alignment" \n')
    lines.append('	 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" \n')
    lines.append('	 xmlns:xsd="http://www.w3.org/2001/XMLSchema#"> \n')
    lines.append('<Alignment>\n')
    lines.append('<xml>yes</xml>\n')
    lines.append('<level>0</level>\n')
    lines.append('<type>??</type>\n')

    for prediction_score in prediction_scores_lines:
        parts = prediction_score.split("|")
        if not parts[0].startswith("i=") or len(parts) != 4:
            continue
        source = parts[1]
        target = parts[2]
        similarity_score = float(parts[3])
        if similarity_score >= threshold:
            lines.append(generate_map_string(source, target, similarity_score))

    lines.append('</Alignment>\n')
    lines.append('</rdf:RDF>\n')

    open(rdf_file_path, 'w').writelines(lines)