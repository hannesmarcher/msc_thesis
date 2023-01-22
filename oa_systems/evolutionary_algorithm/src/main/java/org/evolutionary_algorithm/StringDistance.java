package org.evolutionary_algorithm;

public abstract class StringDistance<T> {

    protected final T similarityMeasure;

    public StringDistance(T similarityMeasure) {
        this.similarityMeasure = similarityMeasure;
    }

    abstract double distance(String s1, String s2);
}
