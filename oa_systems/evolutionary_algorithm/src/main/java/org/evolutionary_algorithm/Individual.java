package org.evolutionary_algorithm;

public class Individual {
    private final SimilarityCalculator similarityCalculator;
    private double[] weights;
    private double thresholdV1;
    private double thresholdV2;
    private double fitness;
    private double probabilityToSurvive = 0;

    public Individual(double[] weights, double thresholdV1, double thresholdV2, SimilarityCalculator similarityCalculator) {
        this.similarityCalculator = similarityCalculator;
        setChromosome(weights, thresholdV1, thresholdV2);
    }

    public void setChromosome(double[] weights, double thresholdV1, double thresholdV2) {
        this.weights = weights;
        this.thresholdV1 = thresholdV1;
        this.thresholdV2 = thresholdV2;
        /*double weights[] = new double[segmentationPoints.length + 1];
        var previousSegPoint = 0.0;
        for (int i = 0; i < segmentationPoints.length; i++) {
            weights[i] = segmentationPoints[i] - previousSegPoint;
            previousSegPoint = segmentationPoints[i];
        }
        weights[weights.length - 1] = 1 - segmentationPoints[segmentationPoints.length - 1];*/
        fitness = similarityCalculator.calculatePseudoFScore(weights, thresholdV1, thresholdV2);
    }

    public double getFitness() {
        return fitness;
    }

    public double getProbabilityToSurvive() {
        return probabilityToSurvive;
    }

    public double[] getWeights() {
        return weights;
    }

    public double getThresholdV1() {
        return thresholdV1;
    }

    public double getThresholdV2() {
        return thresholdV2;
    }

    public void updateFitnessWithAttenuationFactor(double factor) {
        probabilityToSurvive = Math.pow(fitness, factor);
    }
}
