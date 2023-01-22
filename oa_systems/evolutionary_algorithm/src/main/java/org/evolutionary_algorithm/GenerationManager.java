package org.evolutionary_algorithm;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class GenerationManager {

    private final List<Individual> population;
    private final CrossoverCalculator crossoverCalculator;
    private double gOld;
    private double gNew;
    private final MutationCalculator mutationCalculator;
    private final double t;
    private final double theta;
    private final Random random;

    public GenerationManager(
            List<Individual> initialPopulation,
            CrossoverCalculator crossoverCalculator,
            MutationCalculator mutationCalculator,
            double t,
            double theta,
            Random random) {
        this.population = initialPopulation;
        this.crossoverCalculator = crossoverCalculator;
        this.mutationCalculator = mutationCalculator;
        this.t = t;
        this.theta = theta;
        this.random = random;
        updatePopulationFitness();
    }

    private void updatePopulationFitness() {
        gOld = gNew;
        gNew = 0;
        population.forEach(x -> gNew += x.getFitness());
        System.out.println("Updating population fitness:");
        System.out.println("\tgOld: " + gOld);
        System.out.println("\tgNew: " + gNew);
        System.out.println("Population size: " + population.size());
    }

    private void updateFitnessWithAttenuationFactor(int iterationNum) {
        var factor = Math.exp(-(gNew - gOld)/(iterationNum/t)+theta);
        System.out.println("Current attenuation factor: " + factor);
        population.forEach(x -> x.updateFitnessWithAttenuationFactor(factor));
    }

    public List<Individual> selectMatingCandidates(int iterationNum) {
        updateFitnessWithAttenuationFactor(iterationNum);
        var matingCandidates = new ArrayList<Individual>();
        //var totalAttenuation = population.stream().mapToDouble(Individual::getProbabilityToSurvive).sum();
        for (var individual : population) {
            if (random.nextDouble() < individual.getProbabilityToSurvive()) {
                matingCandidates.add(individual);
            }
        }

        System.out.println("Found # mating candidates: " + matingCandidates.size());

        Collections.shuffle(matingCandidates, random);
        return matingCandidates;
    }

    public List<Individual> performCrossOver(List<Individual> matingCandidates) {
        List<Individual> children = new ArrayList<>();
        for (int i = 1; i < matingCandidates.size(); i++) {
            var newIndividual = crossoverCalculator.mateWithProbability(matingCandidates.get(i-1), matingCandidates.get(i));
            newIndividual.ifPresent(children::add);
        }
        return children;
    }

    public void insertChildrenIntoPopulation(List<Individual> children) {
        var elite = getElite();
        Collections.shuffle(population, random);

        var toRemove = IntStream.range(0, children.size()).mapToObj(population::get).collect(Collectors.toList());
        population.removeAll(toRemove);

        population.addAll(children);

        if (!population.contains(elite)) {
            var worst = getWorst();
            population.remove(worst);
            population.add(elite);
        }
    }

    public void mutate() {
        var elite = getElite();
        population.stream().filter(x -> x != elite).forEach(mutationCalculator::mutate);
    }

    public void finalizeNewPopulation() {
        updatePopulationFitness();
        Function<double[], String> doubleArrayToString = doubles -> Arrays.stream(doubles).mapToObj(String::valueOf).collect(Collectors.joining(","));
        var elite = getElite();
        System.out.println("Current elite:");
        System.out.println("\tFitness: " + elite.getFitness());
        System.out.println("\tweights: " + doubleArrayToString.apply(elite.getWeights()));
        System.out.println("\tthreshold V1: " + elite.getThresholdV1());
        System.out.println("\tthreshold V2: " + elite.getThresholdV2());
    }

    public Individual getElite() {
        var maxFitness = population.stream().mapToDouble(Individual::getFitness).max().getAsDouble();
        return population.stream().filter(x -> x.getFitness() == maxFitness).findFirst().get();
    }

    private Individual getWorst() {
        var maxFitness = population.stream().mapToDouble(Individual::getFitness).min().getAsDouble();
        return population.stream().filter(x -> x.getFitness() == maxFitness).findFirst().get();
    }
}
