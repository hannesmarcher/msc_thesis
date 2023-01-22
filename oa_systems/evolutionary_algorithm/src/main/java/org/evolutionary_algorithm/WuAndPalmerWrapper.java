package org.evolutionary_algorithm;

import edu.uniba.di.lacam.kdde.lexical_db.MITWordNet;
import edu.uniba.di.lacam.kdde.ws4j.similarity.WuPalmer;

public class WuAndPalmerWrapper extends StringDistance<WuPalmer> {

    public WuAndPalmerWrapper() {
        super(new WuPalmer(new MITWordNet()));
    }

    @Override
    public double distance(String s1, String s2) {
        var simScore = 0.0;
        try {
            simScore = similarityMeasure.calcRelatednessOfWords(s1, s2);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
            //See https://github.com/dmeoli/WS4J/issues/8
            //After looking into this issue for some time, it is clear that it occurs whenever the similarity score is above 1 - which is an invalid similarity score, of course
            //I am not sure what is going on here; after inspecting the cases in which this exception occurs, it is obvious that the terms are not equivalent
            simScore = 0.0;
        }
        return simScore;
    }
}
