package org.sanom.preprocessing;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.tartarus.snowball.ext.PorterStemmer;

import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/*
The name of each concept is:
 - tokenized (i.e. names that consist of many words result in a bag of words)
 - all the stopwords are then removed from the resulting bag of words
 - stemming is conducted on all resulting words (optional)
 */
public class Preprocessor {

    private final boolean stemming;

    public Preprocessor(boolean stemming) {
        this.stemming = stemming;
    }

    public List<String> getBagOfWords(String name) {
        try (var standardAnalyzer = new StandardAnalyzer()) {
            List<String> bagOfWords = new ArrayList<>();

            var tokenStream
                    = standardAnalyzer.tokenStream("contents", new StringReader(name));
            var term = tokenStream.addAttribute(CharTermAttribute.class);
            tokenStream.reset();
            while (tokenStream.incrementToken()) {
                bagOfWords.add(term.toString());
            }

            if (stemming) {
                bagOfWords = bagOfWords.stream().map(s -> {
                    PorterStemmer stemmer = new PorterStemmer();
                    stemmer.setCurrent(s);
                    stemmer.stem();
                    return stemmer.getCurrent();
                }).collect(Collectors.toList());
            }

            return bagOfWords;

        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

}
