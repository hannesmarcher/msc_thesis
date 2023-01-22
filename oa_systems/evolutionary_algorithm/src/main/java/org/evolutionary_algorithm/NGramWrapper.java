package org.evolutionary_algorithm;

import info.debatty.java.stringsimilarity.NGram;

public class NGramWrapper extends StringDistance<NGram> {

    public NGramWrapper() {
        super(new NGram(3));
    }

    @Override
    public double distance(String s1, String s2) {
        return 1 - similarityMeasure.distance(s1, s2);
    }
}
