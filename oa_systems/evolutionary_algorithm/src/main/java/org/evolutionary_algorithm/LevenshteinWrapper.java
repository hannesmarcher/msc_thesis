package org.evolutionary_algorithm;

import info.debatty.java.stringsimilarity.Levenshtein;

public class LevenshteinWrapper extends StringDistance<Levenshtein> {

    public LevenshteinWrapper() {
        super(new Levenshtein());
    }

    @Override
    public double distance(String s1, String s2) {
        return 1 - similarityMeasure.distance(s1, s2);
    }
}
