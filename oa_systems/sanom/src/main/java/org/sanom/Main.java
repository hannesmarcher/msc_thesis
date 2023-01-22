package org.sanom;

/*
Code inspired by https://github.com/amiaty/SANOM (this implementation seems not to match the corresponding paper, e.g. no soft tf-idf computation)
(Soft) Tf-IDF construction is according to ....
Re-implementation of:
    @article{mohammadi2019simulated,
        title={Simulated annealing-based ontology matching},
        author={Mohammadi, Majid and Hofman, Wout and Tan, Yao-Hua},
        journal={ACM Transactions on Management Information Systems (TMIS)},
        volume={10},
        number={1},
        pages={1--24},
        year={2019},
        publisher={ACM New York, NY, USA}
    }

Steps before this project can be executed:
* Since Alignment API is not available in maven central, it has to be downloaded
    I had problems when using Alignment API 4.1, thus I used 4.10 (in 4.1 I received org.apache.lucene classes not found exceptions)
    execute align_api/init.sh
* Download wordnet from: https://wordnet.princeton.edu/download/old-versions - version 2.1
    Extract ./WordNet-2.1
 */


//What was added in comparison to the existing implementation at https://github.com/amiaty/SANOM:
// - tokenization, stop word removal, stemming
// - soft tf-idf computation
// - change of number q from 6 to 5% of state
// - using lists instead of sets - to allow names with duplicate words (has an effect on tf-idf computation)
// - randomyGreedyInitial changed to not include scores above similarity scores + added structural similarity measures + shuffled also target concepts
// - the iri.getFragment part is useless if id/name of concepts is not specified by base_iri#fragment
// - use only one threshold value + adding structural similarity with string similarity (as described in paper)


//What are the differences between this implementation and the papaer:
//  - In the paper, the authors state that they store values in the similarity matrix if score is > 0.5, however, here I set it to 0.9 for soft tf-idf and 0.95 for wordnet
//  - In the paper, the fitness is calculated by adding all the individual similarity scores, however, here I use children as additional structural sim score + with weights
//  - Many-To-Many mappings are now possible

/*
Experimental results for cpc2cso and cpc2ccs:
* Levenshtein works better than jaco winkler for ccs and cso
* whether simaluated annealing is done or simply greedy construction makes no difference
* Whether stemming is applied or not makes no difference
* WordNet does not provide any benefits (tested on cpc2ccs and cpc2cso)
 */


import fr.inrialpes.exmo.align.impl.eval.PRecEvaluator;
import fr.inrialpes.exmo.align.impl.renderer.RDFRendererVisitor;
import fr.inrialpes.exmo.align.parser.AlignmentParser;
import info.debatty.java.stringsimilarity.NormalizedLevenshtein;
import info.debatty.java.stringsimilarity.interfaces.NormalizedStringDistance;
import org.sanom.matcher.AlignmentProcess;
import org.sanom.matcher.SimilarityMatrices;
import org.sanom.matcher.SimulatedAnnealing;
import org.sanom.preprocessing.Preprocessor;
import org.sanom.similarity.SimilarityMetric;
import org.semanticweb.owl.align.Alignment;
import org.semanticweb.owl.align.AlignmentVisitor;
import org.semanticweb.owl.align.Evaluator;

import java.io.*;
import java.net.URI;
import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        try {

            URI sourceUri = null;
            URI targetUri = null;
            Boolean wordnet = null;
            Double threshold = null;
            String referenceAlignmentFilepath = null;
            String outputFilepath = null;
            for (int i = 0; i < args.length; i += 2) {
                switch (args[i]) {
                    case "--source":
                        sourceUri = new URI("file:" + args[i + 1]);
                        break;
                    case "--target":
                        targetUri = new URI("file:" + args[i + 1]);
                        break;
                    case "--wordnet":
                        wordnet = Boolean.parseBoolean(args[i + 1]);
                        break;
                    case "--threshold":
                        threshold = Double.parseDouble(args[i + 1]);
                        break;
                    case "--reference":
                        referenceAlignmentFilepath = args[i + 1];
                        break;
                    case "--output":
                        outputFilepath = args[i + 1];
                        break;
                }
            }

            if (threshold == null | wordnet == null) {
                try (Scanner sc = new Scanner(new FileInputStream("./config_dir/config.txt"))) {
                    while (sc.hasNextLine()) {
                        var keyValue = sc.nextLine().split("=", 2);
                        if (keyValue[0].equals("wordnet") && wordnet == null)
                            wordnet = Boolean.parseBoolean(keyValue[1]);
                        else if (keyValue[0].equals("threshold") && threshold == null)
                            threshold = Double.parseDouble(keyValue[1]);
                    }
                }
            }

            if (sourceUri == null || targetUri == null || outputFilepath == null || wordnet == null || threshold == null) {
                System.out.println("ERROR: please provide all mandatory arguments!");
                return;
            }

            var algos = new ArrayList<NormalizedStringDistance>();
            //algos.add(new JaroWinkler(0.9));
            algos.add(new NormalizedLevenshtein()); //Levenshtein is much faster

            AlignmentProcess matcher = new AlignmentProcess(sourceUri, targetUri);
            SimilarityMatrices similarityMatrices = matcher.getSimilarityMatrices(
                    new Preprocessor(true),
                    new SimilarityMetric(algos,  wordnet, false),
                    "tmp/similarities" + System.currentTimeMillis() + ".txt"
            );

            /*var maxFmeasure = 0.0;
            var bestThreshold = 0.0;
            for (threshold = 0.9; threshold < 4.0; threshold += 0.1) {*/
                System.out.println("-----------------------------------------------------");
                System.out.println("Threshold: " + threshold);
                matcher = new AlignmentProcess(sourceUri, targetUri);
                double finalThreshold = threshold;
                matcher.computeAlignment(() -> new SimulatedAnnealing(
                        similarityMatrices.getSimilarity(),
                        similarityMatrices.getSupSimilarity(),
                        similarityMatrices.getSubSimilarity(),
                        100,
                        finalThreshold
                ));

                //File alignmentFile = File.createTempFile("alignment", ".rdf");
                File alignmentFile = new File(outputFilepath);
                FileWriter fw = new FileWriter(alignmentFile);
                PrintWriter pw = new PrintWriter(fw);
                AlignmentVisitor rendererVisitor = new RDFRendererVisitor(pw);
                matcher.render(rendererVisitor);
                fw.flush();
                fw.close();
                System.out.println(alignmentFile.toURI().toURL());

                if (referenceAlignmentFilepath != null) {
                    System.out.println("Perform evaluation...");
                    // eval
                    AlignmentParser alignmentParser = new AlignmentParser(0);
                    Alignment ref = alignmentParser.parse("file:" + referenceAlignmentFilepath);
                    ref.init(sourceUri, targetUri);
                    ref.harden(0.01);
                    Evaluator evaluator = new PRecEvaluator(ref, matcher);
                    evaluator.eval(System.getProperties());
                    /*if (maxFmeasure < Double.parseDouble(evaluator.getResults().get("fmeasure").toString())) {
                        maxFmeasure = Double.parseDouble(evaluator.getResults().get("fmeasure").toString());
                        bestThreshold = threshold;
                    }*/
                    System.out.println(evaluator.getResults().toString());
                }

            /*}

            System.out.println("Best threshold: " + bestThreshold + " with f-score: " + maxFmeasure);*/


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}