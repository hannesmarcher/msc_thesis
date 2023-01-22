package org.sanom.matcher;

public class SimilarityMatrices {
    private final double[][] similarity;
    private final double[][] supSimilarity;
    private final double[][] subSimilarity;

    public SimilarityMatrices(double[][] similarity, double[][] supSimilarity, double[][] subSimilarity) {
        this.similarity = similarity;
        this.supSimilarity = supSimilarity;
        this.subSimilarity = subSimilarity;
    }

    public double[][] getSimilarity() {
        return similarity;
    }

    public double[][] getSupSimilarity() {
        return supSimilarity;
    }

    public double[][] getSubSimilarity() {
        return subSimilarity;
    }
}
