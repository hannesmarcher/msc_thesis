package org.evolutionary_algorithm;

import java.util.Optional;
import java.util.Random;

public class CrossoverCalculator {

    private final double crossOverProbability;
    private final SimilarityCalculator similarityCalculator;
    private final Random random;

    public CrossoverCalculator(double crossOverProbability, SimilarityCalculator similarityCalculator, Random random) {
        this.crossOverProbability = crossOverProbability;
        this.similarityCalculator = similarityCalculator;
        this.random = random;
    }

    public Optional<Individual> mateWithProbability(Individual individual1, Individual individual2) {
        if (random.nextDouble() >= crossOverProbability) {
            //Different cross-over operator (when compared to paper
            double[] newWeights = new double[individual1.getWeights().length];
            for (int i = 0; i < newWeights.length; i++) {
                if (i % 2 == 0)
                    newWeights[i] = individual1.getWeights()[i];
                else
                    newWeights[i] = individual2.getWeights()[i];
            }
            return Optional.of(new Individual(newWeights, individual1.getThresholdV1(), individual2.getThresholdV2(), similarityCalculator));
        }


        return Optional.empty();
    }
}
