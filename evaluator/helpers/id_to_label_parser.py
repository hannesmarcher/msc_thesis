def parse_tuples_to_first_label(tuples, onto_cpc, onto_other):
    label_tuples = []
    for (e1, e2) in tuples:
        e1_class = onto_cpc.search(iri=e1)
        e2_class = onto_other.search(iri=e2)
        assert len(e1_class) == 1
        assert len(e2_class) == 1
        labels_e1 = getattr(e1_class[0], "label")
        labels_e2 = getattr(e2_class[0], "label")
        # check if CCS or CSO (in case of CSO use iri, otherwise ambiguous
        if len(labels_e2) == 1:
            label_tuples.append((labels_e1[0], labels_e2[0]))
        else:
            label_tuples.append((labels_e1[0], e2[::-1].split("/", 1)[0][::-1].replace("_", " ")))

    return label_tuples