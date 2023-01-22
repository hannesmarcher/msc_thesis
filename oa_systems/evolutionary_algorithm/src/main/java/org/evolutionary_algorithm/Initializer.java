package org.evolutionary_algorithm;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Initializer {
    private final int initialPopulation;
    private final SimilarityCalculator similarityCalculator;
    private final Random random;

    public Initializer(int initialPopulation, SimilarityCalculator similarityCalculator, Random random) {
        this.initialPopulation = initialPopulation;
        this.similarityCalculator = similarityCalculator;
        this.random = random;
    }

    public List<Individual> init() {
        List<Individual> population = new ArrayList<>();
        for (int i = 0; i < initialPopulation; i++) {
            double[] weights = new double[similarityCalculator.getNumSimMeasures()];
            for (int j = 0; j < weights.length; j++)
                weights[j] = random.nextDouble();
            double thresholdV1 = random.nextDouble();
            double thresholdV2 = random.nextDouble();
            population.add(new Individual(weights, thresholdV1, thresholdV2, similarityCalculator));
        }
        return population;
    }
}
