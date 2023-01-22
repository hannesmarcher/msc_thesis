package org.evolutionary_algorithm;

import info.debatty.java.stringsimilarity.JaroWinkler;

public class JaroWinklerWrapper extends StringDistance<JaroWinkler> {
    public JaroWinklerWrapper() {
        super(new JaroWinkler(0.9));
    }

    @Override
    double distance(String s1, String s2) {
        return 1 - similarityMeasure.distance(s1, s2);
    }
}
