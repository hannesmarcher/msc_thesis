package org.baseline;

import de.uni_mannheim.informatik.dws.melt.matching_jena.MatcherYAAAJena;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.vocabulary.RDFS;

import java.util.*;
import java.util.stream.Collectors;

public class BaselineMatcher extends MatcherYAAAJena {

    @Override
    public Alignment match(OntModel source, OntModel target, Alignment alignment, Properties properties) throws Exception {

        System.out.println("Staring baseline matcher");

        var uriOntoClazzListSource = readUriOntoClassList(source);
        var uriOntoClazzListTarget = readUriOntoClassList(target);

        Set<Tuple<String, String>> correspondences = new HashSet<>();
        var labelToIriMapSource = buildLabelIriMap(uriOntoClazzListSource);
        System.out.println("Label IRI Map built");

        for (OntoClazz ontoClazzTarget : uriOntoClazzListTarget) {
            for (var label : ontoClazzTarget.labels) {
                if (labelToIriMapSource.containsKey(label.toLowerCase())) {
                    var listOfIris = labelToIriMapSource.get(label.toLowerCase());
                    listOfIris.forEach(x -> correspondences.add(new Tuple<>(x, ontoClazzTarget.uri)));
                }
            }
        }
        var result = new Alignment();
        correspondences.forEach(x -> result.add(x.getT1(), x.getT2()));
        return result;
    }

    private Map<String, List<String>> buildLabelIriMap(List<OntoClazz> ontoClazzList) {
        Map<String, List<String>> map = new HashMap<>();
        for (var clazz : ontoClazzList) {
            for (var label : clazz.labels) {
                map.putIfAbsent(label.toLowerCase(), new ArrayList<>());
                map.get(label.toLowerCase()).add(clazz.uri);
            }
        }
        return map;
    }

    private List<OntoClazz> readUriOntoClassList(OntModel model) {
        List<OntoClazz> uriOntoClazzList = new ArrayList<>();
        for (var clazz : model.listClasses().toList()) {
            var uri = clazz.getURI();
            var labels = clazz.listProperties(RDFS.label).toList()
                    .stream().map(x -> x.getLiteral().getString().toLowerCase()).collect(Collectors.toList());
            uriOntoClazzList.add(new OntoClazz(
                    uri,
                    labels
            ));
        }
        return uriOntoClazzList;
    }

    private static class OntoClazz {
        private final String uri;
        private final List<String> labels;

        OntoClazz(String uri, List<String> labels) {
            this.uri = uri;
            this.labels = labels;
        }
    }
}
