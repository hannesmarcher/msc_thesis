package org.evolutionary_algorithm;

import de.uni_mannheim.informatik.dws.melt.matching_jena.MatcherYAAAJena;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.vocabulary.RDFS;

import java.util.*;
import java.util.stream.Collectors;

public class EvolutionaryAlgorithmMatcher extends MatcherYAAAJena {

    @Override
    public Alignment match(OntModel source, OntModel target, Alignment alignment, Properties properties) throws Exception {
        var sourceClasses = getAllClasses(source);
        var targetClasses = getAllClasses(target);

        Random random = new Random(123);

        SimilarityCalculator similarityCalculator = new SimilarityCalculator(List.of(
                new NGramWrapper(),
                new WuAndPalmerWrapper()
        ));
        similarityCalculator.constructSimMatrices(sourceClasses, targetClasses);
        System.out.println("Similarity matrix calculation finished....");

        Initializer initializer = new Initializer(100, similarityCalculator, random);
        List<Individual> population = initializer.init();

        CrossoverCalculator crossoverCalculator = new CrossoverCalculator(0.5, similarityCalculator, random);
        MutationCalculator mutationCalculator = new MutationCalculator(0.01, random);
        GenerationManager generationManager = new GenerationManager(population, crossoverCalculator, mutationCalculator, 10, 0, random);

        for (int iter = 0; iter < 10; iter++) {
            System.out.println("Current iteration: " + iter);
            var matingCandidates = generationManager.selectMatingCandidates(iter);
            generationManager.insertChildrenIntoPopulation(generationManager.performCrossOver(matingCandidates));
            generationManager.mutate();
            generationManager.finalizeNewPopulation();
        }

        AlignmentGenerator alignmentGenerator = new AlignmentGenerator(0.9);
        return alignmentGenerator.getAlignment(sourceClasses, targetClasses, generationManager.getElite(), similarityCalculator);
    }

    private List<OntoClazz> getAllClasses(OntModel model) {
        List<OntoClazz> classList = new ArrayList<>();
        int i = 0;
        for (var clazz : model.listClasses().toList()) {
            var uri = clazz.getURI();
            if (uri == null)
                continue; //Anatomy
            var labels = clazz.listProperties(RDFS.label).toList()
                    .stream().map(x -> x.getLiteral().getString().toLowerCase()).collect(Collectors.toList());
            var comments = clazz.listProperties(RDFS.comment).toList()
                    .stream().map(x -> x.getLiteral().getString().toLowerCase()).collect(Collectors.toList());
            classList.add(new OntoClazz(
                    i,
                    uri,
                    labels,
                    comments
            ));
            i++;
        }
        return classList;
    }

}
