package org.evolutionary_algorithm;

import java.util.ArrayList;
import java.util.List;

public class SimilarityCalculator {

    private List<double[][]> simMatricesId;
    private List<double[][]> simMatricesLabel;

    private final List<StringDistance<?>> similarityMeasures;

    public SimilarityCalculator(List<StringDistance<?>> similarityMeasures) {
        this.similarityMeasures = similarityMeasures;
        simMatricesId = new ArrayList<>();
        simMatricesLabel = new ArrayList<>();
    }

    public int getNumSimMeasures() {
        return similarityMeasures.size();
    }

    public void constructSimMatrices(List<OntoClazz> sourceClasses, List<OntoClazz> targetClasses) {

        for (var ignored : similarityMeasures) {
            simMatricesId.add(new double[sourceClasses.size()][targetClasses.size()]);
            simMatricesLabel.add(new double[sourceClasses.size()][targetClasses.size()]);
        }

        for (var sourceClass : sourceClasses) {
            for (var targetClass : targetClasses) {
                int i = sourceClass.getInternalId();
                int j = targetClass.getInternalId();
                for (int similarityMeasureIndex = 0; similarityMeasureIndex < similarityMeasures.size(); similarityMeasureIndex++) {
                    simMatricesId.get(similarityMeasureIndex)[i][j] = similarityMeasures.get(similarityMeasureIndex).distance(sourceClass.getId(), targetClass.getId());
                    for (var label1 : sourceClass.getLabels()) {
                        for (var label2 : targetClass.getLabels()) {
                            simMatricesId.get(similarityMeasureIndex)[i][j] = similarityMeasures.get(similarityMeasureIndex).distance(label1, label2);
                        }
                    }

                }
            }
        }
        System.out.println();
    }

    public double getSimilarityScore(int internalId1, int internalId2, double[] weights, double thresholdV1, double thresholdV2) {
        var similarityId = 0.0;
        if (weights.length != similarityMeasures.size())
            System.out.println("WARNING: something went wrong");
        for (int i = 0; i < weights.length; i++)
            similarityId = weights[i] * simMatricesId.get(i)[internalId1][internalId2];
        if (similarityId >= thresholdV1)
            return similarityId;

        var similarityLabel = 0.0;
        for (int i = 0; i < weights.length; i++)
            similarityLabel = weights[i] * simMatricesLabel.get(i)[internalId1][internalId2];
        if (similarityLabel >= thresholdV2)
            return similarityLabel;
        return 0.0;
    }

    private double[] getMaxRow(double[] weights, double thresholdV1, double thresholdV2) {
        double[] maxRow = new double[simMatricesId.get(0).length];
        for (int i = 0; i < maxRow.length; i++) {
            double maxValue = 0.0;
            for (int j = 0; j < simMatricesId.get(0)[0].length; j++) {
                maxValue = Math.max(getSimilarityScore(i, j,  weights, thresholdV1, thresholdV2), maxValue);
            }
            maxRow[i] = maxValue;
        }
        return maxRow;
    }

    private double[] getMaxColumn(double[] weights, double thresholdV1, double thresholdV2) {
        double[] maxColumn = new double[simMatricesId.get(0)[0].length];
        for (int i = 0; i < maxColumn.length; i++) {
            double maxValue = 0.0;
            for (int j = 0; j < simMatricesId.get(0).length; j++) {
                maxValue = Math.max(getSimilarityScore(j, i,  weights, thresholdV1, thresholdV2), maxValue);
            }
            maxColumn[i] = maxValue;
        }
        return maxColumn;
    }

    private int getCounter(double[] maxRow, double[] maxColumn, double[] weights, double thresholdV1, double thresholdV2) {
        var counter  = 0;
        for (int i = 0; i < maxRow.length; i++) {
            for (int j = 0; j < maxColumn.length; j++) {
                var similarity = getSimilarityScore(i, j,  weights, thresholdV1, thresholdV2);
                if (similarity == maxRow[i] && similarity == maxColumn[j]) {
                    counter++;
                    break;
                }
            }
        }
        return counter;
    }

    private double calculatePseudoRecall(double[] weights, double thresholdV1, double thresholdV2) {
        double[] maxRow = getMaxRow(weights, thresholdV1, thresholdV2);
        double[] maxColumn = getMaxColumn(weights, thresholdV1, thresholdV2);

        var counter = getCounter(maxRow, maxColumn, weights, thresholdV1, thresholdV2);

        var minSize = Math.min(simMatricesId.get(0).length, simMatricesId.get(0)[0].length);

        return (double) counter / minSize;
    }

    private double getConfidence(double[] maxRow, double[] maxColumn, double[] weights, double thresholdV1, double thresholdV2) {
        var confidence  = 0.0;
        for (int i = 0; i < maxRow.length; i++) {
            for (int j = 0; j < maxColumn.length; j++) {
                var similarity = getSimilarityScore(i, j,  weights, thresholdV1, thresholdV2);
                if (similarity == maxRow[i] && similarity == maxColumn[j]) {
                    confidence += similarity;
                    break;
                }
            }
        }
        return confidence;
    }

    private double calculatePseudoPrecision(double[] weights, double thresholdV1, double thresholdV2) {
        double[] maxRow = getMaxRow(weights, thresholdV1, thresholdV2);
        double[] maxColumn = getMaxColumn(weights, thresholdV1, thresholdV2);

        var counter = getCounter(maxRow, maxColumn, weights, thresholdV1, thresholdV2);

        //TODO how to do if multiple entity matching pairs are found that -> atm always the first is taken, however, that might not be optimal

        var confidence = getConfidence(maxRow, maxColumn, weights, thresholdV1, thresholdV2);

        return confidence / counter;
    }

    public double calculatePseudoFScore(double[] weights, double thresholdV1, double thresholdV2) {
        var precision = calculatePseudoPrecision(weights, thresholdV1, thresholdV2);
        var recall = calculatePseudoRecall(weights, thresholdV1, thresholdV2);
        //TODO try to overweight precision
        return 2 * recall * precision / (recall + precision);
    }

}
