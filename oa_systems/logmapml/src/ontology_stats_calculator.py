from owlready2 import get_ontology, IndividualValueList, entity, owl


def get_path_size_max_token_length(source_onto_path: str, target_onto_path) -> (int, int, int, int):
    onto_source = get_ontology(source_onto_path).load()
    onto_target = get_ontology(target_onto_path).load()

    source_depth_map = dict()
    max_token_length_source = 0
    for clazz in onto_source.classes():
        source_depth_map[clazz.iri] = -1
        values = getattr(clazz, "label")
        assert type(values) is IndividualValueList
        for value in values:
            max_token_length_source = max(max_token_length_source, len(value))

    target_depth_map = dict()
    max_token_length_target = 0
    for clazz in onto_target.classes():
        target_depth_map[clazz.iri] = -1
        values = getattr(clazz, "label")
        assert type(values) is IndividualValueList
        for value in values:
            max_token_length_target = max(max_token_length_target, len(value))

    for clazz in onto_source.classes():
        _compute_depth(clazz, source_depth_map)

    for clazz in onto_target.classes():
        _compute_depth(clazz, target_depth_map)

    return max(source_depth_map.values()), max_token_length_source, max(target_depth_map.values()), max_token_length_target


def _compute_depth(clazz, depth_map):
    if depth_map[clazz.iri] != -1:
        return
    super_classes = []
    for super_class in clazz.is_a:
        if type(super_class) == entity.ThingClass:
            super_classes.append(super_class)

    if owl.Thing in super_classes or len(super_classes) == 0:
        depth_map[clazz.iri] = 0
    else:
        current_depth = -1
        for super_class in super_classes:
            _compute_depth(super_class, depth_map)
            current_depth = max(current_depth, depth_map[super_class.iri] + 1)
        depth_map[clazz.iri] = current_depth
