package org.sanom.similarity;

import info.debatty.java.stringsimilarity.interfaces.NormalizedStringDistance;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/*
 Implementation of Soft TF-IDF is based on "A comparative evaluation of string similarity metrics for ontology alignment" Sun Y, Ma L et. al. 2015
 TF-IDF implementation is based on "Ontology Matching Using TF/IDF Measure  with Synonym Recognition" Gulić M, Magdalenić I, Vrdoljak B 2013
 */
public class SimilarityMetric {

    private List<List<String>> allStrings1;
    private List<List<String>> allStrings2;
    private final Map<String, Set<String>> wordToSimilarWordsMap1; //key: each word in O1; value: similar words in O2
    private final Map<String, Map<String, Double>> c; //In the SANOM paper this is referred to as C
    private final List<NormalizedStringDistance> stringSimilarityMeasures;
    private WuAndPalmerWrapper wuAndPalmerWrapper = null;
    private final boolean logging;

    private static final Logger LOGGER = Logger.getLogger(SimilarityMetric.class.getSimpleName());

    public SimilarityMetric(
            List<NormalizedStringDistance> stringSimilarityMeasures,
            boolean useWordnet,
            boolean logging
    ) {
        this.stringSimilarityMeasures = stringSimilarityMeasures;
        this.logging = logging;
        wordToSimilarWordsMap1 = new HashMap<>();

        c = new HashMap<>();

        if (useWordnet)
            wuAndPalmerWrapper = new WuAndPalmerWrapper();

    }

    public void init(
            List<List<String>> allStrings1,
            List<List<String>> allStrings2

    ) {
        this.allStrings1 = allStrings1;
        this.allStrings2 = allStrings2;
        initC();

    }

    private void initC() {
        System.out.println("intialiazing C...");
        Set<String> allWords1 = allStrings1.stream().flatMap(Collection::stream).collect(Collectors.toSet());
        Set<String> allWords2 = allStrings2.stream().flatMap(Collection::stream).collect(Collectors.toSet());
        var counter = 0;
        for (var word1 : new HashSet<>(allWords1)) {
            wordToSimilarWordsMap1.put(word1, new HashSet<>());
            c.put(word1, new HashMap<>());
            for (var word2 : new HashSet<>(allWords2)) {
                var similarity = getSimilarityScore(word1, word2);
                if (similarity >= 0.9) {
                    wordToSimilarWordsMap1.get(word1).add(word2);
                    c.get(word1).put(word2, similarity);
                } else if (wuAndPalmerWrapper != null) {
                    similarity = wuAndPalmerWrapper.distance(word1, word2);
                    if (similarity >= 0.95)
                        c.get(word1).put(word2, similarity);
                }
            }
            counter++;
            System.out.printf("\r%.0f%% completed!", (double)counter/allWords1.size() * 100);
        }
        System.out.println();
    }

    /**
     * Note this implementation allows values greater than 1.0 since we divide through sqrt in V
     * @param string1
     * @param string2
     * @return
     */
    public double getSimilarityMetric(List<String> string1, List<String> string2) {
        //return stringSimilarityMeasures.stream().mapToDouble(x -> x.distance(string1.get(0), string2.get(0))).average().getAsDouble();
        Set<String> string1DuplicatesRemoved = new HashSet<>(string1);
        Set<String> string2DuplicatesRemoved = new HashSet<>(string2);

        double score = 0.0;

        for (var word1 : string1DuplicatesRemoved) {

            double maxSimilarity = 0.0;
            String maxWord2 = null;
            for (var word2 : string2DuplicatesRemoved) {
                if (wordToSimilarWordsMap1.get(word1).contains(word2)) {
                    var similarity = c.get(word1).get(word2);
                    if (maxSimilarity < similarity) {
                        maxWord2 = word2;
                        maxSimilarity = similarity;
                    }
                }
            }

            if (maxWord2 != null) {
                var similarity = getV(word1, string1, allStrings1) * getV(maxWord2, string2, allStrings2) * maxSimilarity;
                score += similarity;
            }
        }

        if (logging && score >= 0.72)
            LOGGER.log(Level.INFO, String.format("\tFound strong correlation: The two strings %s %s is assigned score %s", string1, string2, score));

        return score;
    }

    private double getSimilarityScore(String word1, String word2) {
        double similarity = 0.0;
        for (var algo : stringSimilarityMeasures) {
            similarity = Math.max(similarity, 1.0 - algo.distance(word1, word2));
        }

        return similarity;
    }


    private double getTermFrequency(String word, List<String> string) {
        // frequency of a term in document / frequency of most appearing term in same document
        // according to Wikipedia double normalization makes sense when dividing through the most frequently occurring term
        return 0.5 + 0.5 * (double) string.stream().filter(x -> x.equals(word)).count() /
                string.stream().mapToInt(x -> string.stream().mapToInt(x2 -> string.contains(x2) ? 1 : 0).sum()).max().getAsInt();
    }

    private double getInverseDocumentFrequency(String word, List<List<String>> allStrings) {
        return (double) allStrings.size() / allStrings.stream().filter(x -> x.contains(word)).count();
    }

    private double getV(String word, List<String> string, List<List<String>> allStrings){
        return getVPrime(word, string, allStrings) / Math.sqrt(string.stream().mapToDouble(x -> getVPrime(x, string, allStrings)).sum());
        //return getVPrime(word, string, allStrings) / string.stream().mapToDouble(x -> getVPrime(x, string, allStrings)).sum();
    }

    private double getVPrime(String word, List<String> string, List<List<String>> allStrings) {
        return Math.log(getTermFrequency(word, string) + 1) * Math.log(getInverseDocumentFrequency(word, allStrings));
    }
}
