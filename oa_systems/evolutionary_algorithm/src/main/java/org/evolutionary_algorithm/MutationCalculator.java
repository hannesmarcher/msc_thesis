package org.evolutionary_algorithm;

import java.util.Random;
import java.util.function.DoubleSupplier;

public class MutationCalculator {

    private final double probability;
    private final Random random;

    public MutationCalculator(double probability, Random random) {
        this.probability = probability;
        this.random = random;
    }

    public void mutate(Individual individual) {

        DoubleSupplier offsetGenerator = () -> {
            var offset = random.nextDouble();
            var sign = random.nextBoolean();
            return sign ? offset : -offset;
        };

        //This here deviates from the paper since the related section in the paper describes muation of binary encoded chromosomes, however, here we don't have binary encodings
        //Here, we simply alter each entry of a chromosome by a random uniform sample
        if (random.nextDouble() < probability) {
            System.out.println("performing mutation...");
            double[] newWeights = new double[individual.getWeights().length];
            for (int i = 0; i < newWeights.length; i++) {
                var newValue = individual.getWeights()[i] + offsetGenerator.getAsDouble();
                if (newValue >= 0.0 && newValue <= 1.0)
                    newWeights[i] = newValue;
                else
                    newWeights[i] = individual.getWeights()[i];
            }
            var newThreshold1 = individual.getThresholdV1() + offsetGenerator.getAsDouble();
            var newThreshold2 = individual.getThresholdV2() + offsetGenerator.getAsDouble();
            individual.setChromosome(
                    newWeights,
                    newThreshold1 > 1.0 || newThreshold1 < 0 ? individual.getThresholdV1() : newThreshold1,
                    newThreshold2 > 1.0 || newThreshold2 < 0 ? individual.getThresholdV2() : newThreshold2
            );
        }
    }
}
