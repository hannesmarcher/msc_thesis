package org.meta_matcher;

import de.uni_mannheim.informatik.dws.melt.matching_jena.MatcherYAAAJena;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;
import edu.uniba.di.lacam.kdde.lexical_db.ILexicalDatabase;
import edu.uniba.di.lacam.kdde.lexical_db.MITWordNet;
import edu.uniba.di.lacam.kdde.ws4j.similarity.WuPalmer;
import info.debatty.java.stringsimilarity.Cosine;
import info.debatty.java.stringsimilarity.NGram;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.vocabulary.RDFS;

import java.util.*;
import java.util.stream.Collectors;

public class LxlhMetaMatcher extends MatcherYAAAJena {

    @Override
    public Alignment match(OntModel source, OntModel target, Alignment alignment, Properties properties) {

        Map<String, OntoClazz> uriOntoClazzMap1 = readUriOntoClassMap(source);
        Map<String, OntoClazz> uriOntoClazzMap2 = readUriOntoClassMap(target);

        var threshold = 0.9;
        var thresholdIfWordnetNotAvailable = 0.95;
        Set<Triple<String, String, Double>> N = new HashSet<>(); //N-gram set
        Set<Triple<String, String, Double>> W = new HashSet<>(); //Wu and Palmer Set

        NGram nGram = new NGram(3);
        Cosine cosine = new Cosine();
        ILexicalDatabase lexicalDatabase = new MITWordNet();
        WuPalmer wuPalmer = new WuPalmer(lexicalDatabase);

        double progressStep = 100.0 / uriOntoClazzMap1.size();
        double progress = progressStep;
        for (OntoClazz ontoClazz1 : uriOntoClazzMap1.values()) {
            for (OntoClazz ontoClazz2 : uriOntoClazzMap2.values()) {
                var maxSimNgram = 0.0;
                var maxWuPalmer = 0.0;
                var maxCosine = 0.0;
                for (var label1 : ontoClazz1.labels) {
                    for (var label2 : ontoClazz2.labels) {
                        maxSimNgram = Math.max(maxSimNgram, 1 - nGram.distance(label1, label2));
                        maxCosine = Math.max(maxCosine, 1 - cosine.distance(label1, label2));
                        try {
                            if (maxWuPalmer < 1.0)
                                maxWuPalmer = Math.max(maxWuPalmer, wuPalmer.calcRelatednessOfWords(label1, label2));
                        } catch (IllegalArgumentException e) {
                            //See https://github.com/dmeoli/WS4J/issues/8
                            //After looking into this issue for a some time, it is clear that it occurs whenever the similarity score is above 1 - which is an invalid similairty score
                            //I am not sure what is going on here and after inspecting the cases in which this exception occurs, it is obvious that the terms are not equivalent
                            maxWuPalmer = 0.0;
                        }
                    }
                }
                if (maxSimNgram >= threshold)
                    N.add(new Triple<>(ontoClazz1.uri, ontoClazz2.uri, maxSimNgram));
                // (Cosine is added here (deviates from paper))
                //if (maxCosine >= threshold)
                //    N.add(new Triple<>(ontoClazz1.uri, ontoClazz2.uri, maxCosine));

                //Calculate Wu & Palmer only if there is one label per concept and the respective label consists of one word
                if (ontoClazz1.labels.size() == ontoClazz2.labels.size() && ontoClazz1.labels.size() == 1) {
                    var words1 = ontoClazz1.labels.get(0).trim().split("\\s+");
                    var words2 = ontoClazz2.labels.get(0).trim().split("\\s+");
                    if (words1.length == 1 && words2.length == 1) {
                        try {
                            var simScore = wuPalmer.calcRelatednessOfWords(words1[0], words2[0]);
                            if (simScore >= threshold)
                                W.add(new Triple<>(ontoClazz1.uri, ontoClazz2.uri, simScore));
                        } catch (IllegalArgumentException e) {
                            //See https://github.com/dmeoli/WS4J/issues/8
                            W.add(new Triple<>(ontoClazz1.uri, ontoClazz2.uri, 0.0));
                        }
                    }
                }
            }
            System.out.printf("\r%.0f%% completed!", progress);
            progress += progressStep;
        }

        //To check for case 1, it is necessary to compute the intersection between N and W
        //map to similarity 0, such that .equals returns true if t1 and t2 match
        Set<Triple<String, String, Double>> intersection = N.stream()
                .map(x -> new Triple<>(x.getT1(), x.getT2(), 1.0))
                .filter(x -> W.stream().map(x1 -> new Triple<>(x1.getT1(), x1.getT2(), 1.0))
                        .anyMatch(x1 -> x1.equals(x)))
                .collect(Collectors.toSet());

        //determine which entities appear only once in the intersection
        var distinctEntitiesSource = intersection.stream().map(Triple::getT1).collect(Collectors.toSet());
        var distinctEntitiesTarget = intersection.stream().map(Triple::getT2).collect(Collectors.toSet());

        //If a correspondence involves an entity that appears only once and is in the intersection, it shall be included in S
        //matching set
        Set<Triple<String, String, Double>> S = intersection.stream().filter(x -> distinctEntitiesSource.contains(x.getT1()) && distinctEntitiesTarget.contains(x.getT2())).collect(Collectors.toSet());

        var remainingCorrespondences = N.stream().filter(x -> !distinctEntitiesSource.contains(x.getT1()) || !distinctEntitiesTarget.contains(x.getT2()));


        //As in my use case there are no comments, we can skip handling case 2,3,4
        //  Additionally, the IDs in my use case contain no semantic information, therefore it does not make sense to take the average
        //  Instead we use the difference N - W and simply include each correspondence if the similarity is above threshold 0.95 (taken from paper)
        S.addAll(remainingCorrespondences.filter(x -> x.getT3() > thresholdIfWordnetNotAvailable).collect(Collectors.toList()));

        //Note that in contrast to the paper, here, we allow duplications


        var result = new Alignment();
        S.forEach(x -> result.add(x.getT1(), x.getT2(), x.getT3()));

        return result;
    }

    private Map<String, OntoClazz> readUriOntoClassMap(OntModel model) {
        Map<String, OntoClazz> uriOntoClazzMap = new HashMap<>();
        for (var clazz : model.listClasses().toList()) {
            var uri = clazz.getURI();
            var labels = clazz.listProperties(RDFS.label).toList()
                    .stream().map(x -> x.getLiteral().getString().toLowerCase()).collect(Collectors.toList());
            var comments = clazz.listProperties(RDFS.comment).toList()
                    .stream().map(x -> x.getLiteral().getString().toLowerCase()).collect(Collectors.toList());
            var directSuperClasses = clazz.listSuperClasses(true).toList().stream().map(Resource::getURI).collect(Collectors.toList());
            uriOntoClazzMap.put(uri, new OntoClazz(
                    uri,
                    labels,
                    comments,
                    directSuperClasses
            ));
        }
        return uriOntoClazzMap;
    }

    private class OntoClazz {
        private final String uri;
        private final List<String> labels;
        private final List<String> comments;
        private final List<String> parentClassesUris;

        OntoClazz(String uri, List<String> labels, List<String> comments, List<String> parentClassesUris) {
            this.uri = uri;
            this.labels = labels;
            this.comments = comments;
            this.parentClassesUris = parentClassesUris;
        }
    }
}
