package org.evolutionary_algorithm;

import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;

import java.util.List;

public class AlignmentGenerator {

    private final double threshold;

    public AlignmentGenerator(double threshold) {
        this.threshold = threshold;
    }

    public Alignment getAlignment(List<OntoClazz> sourceClasses, List<OntoClazz> targetClasses, Individual elite, SimilarityCalculator similarityCalculator) {
        Alignment alignment = new Alignment();

        //In contrast to the paper - here we do not construct a one-to-one alignment - the following code did generate far too  many false positives at Anatomy
        /*for (OntoClazz sourceClass : sourceClasses) {
            for (OntoClazz targetClass : targetClasses) {
                var simScore = similarityCalculator.getSimilarityScore(
                        sourceClass.getInternalId(),
                        targetClass.getInternalId(),
                        elite.getWeights(),
                        elite.getThresholdV1(),
                        elite.getThresholdV2());
                if (simScore >= threshold) {
                    alignment.add(sourceClass.getUri(), targetClass.getUri(), simScore);
                }
            }
        }*/

        List<OntoClazz> smallerOfTwo = sourceClasses.size() <= targetClasses.size() ? sourceClasses : targetClasses;
        List<OntoClazz> largerOfTwo = sourceClasses.size() > targetClasses.size() ? sourceClasses : targetClasses;
        boolean isSmallerSource = smallerOfTwo.equals(sourceClasses);
        for (OntoClazz clazz1 : smallerOfTwo) {
            var maxSimScore = 0.0;
            Triple<String, String, Double> correspondence = null;
            for (OntoClazz clazz2 : largerOfTwo) {
                var sourceClazz = isSmallerSource ? clazz1 : clazz2;
                var targetClazz = isSmallerSource ? clazz2 : clazz1;
                var simScore = similarityCalculator.getSimilarityScore(
                        sourceClazz.getInternalId(),
                        targetClazz.getInternalId(),
                        elite.getWeights(),
                        elite.getThresholdV1(),
                        elite.getThresholdV2());
                if (simScore >= threshold) {
                    if (simScore > maxSimScore) {
                        maxSimScore = simScore;
                        correspondence = new Triple<>(sourceClazz.getUri(), targetClazz.getUri(), simScore);
                    }
                }
            }
            if (correspondence != null)
                alignment.add(correspondence.getT1(), correspondence.getT2(), correspondence.getT3());
        }

        return alignment;
    }
}
