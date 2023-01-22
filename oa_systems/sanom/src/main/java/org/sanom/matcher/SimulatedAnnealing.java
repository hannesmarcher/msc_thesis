package org.sanom.matcher;

import org.sanom.util.Triple;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

public class SimulatedAnnealing implements IAlignmentMethod {
    private final double[][] similarity;
    private final double[][] similarityStructural;
    private final double[][] similarityChildren;
    private final List<Integer> solSource;
    private final List<Integer> solTarget;
    private double fitness;
    private final int row;
    private final int col;
    private final int duration;
    private final double threshold;
    private final Random random;

    public SimulatedAnnealing(double[][] sim, double[][] simStructural, double[][] simChildren, int duration, double threshold) {
        similarity = sim;
        similarityStructural = simStructural;
        similarityChildren = simChildren;
        row = sim.length;
        col = sim[0].length;
        this.duration = duration;
        this.threshold = threshold;
        //random = new Random(System.currentTimeMillis());
        random = new Random(0);
        solSource = new ArrayList<>();
        solTarget = new ArrayList<>();
    }

    private void solve() {
        double deltaE, temperature = 1.0, alpha = 0.998;
        randomGreedyInitTechnique();
        updateFitness();
        for (int t = 0; t < duration; t++) {
            var currentSolution = new ArrayList<>(solSource);
            var currentFitness = fitness;
            for (int j = 0; j < 100; j++) {
                var successor = generateSuccessor(currentSolution);
                var fitNext = computeFitness(successor);
                deltaE = fitNext - fitness;
                if (deltaE > 0 || random.nextDouble() >= Math.exp(deltaE / temperature)) {
                    currentSolution.clear();
                    currentSolution.addAll(successor);
                    currentFitness = fitNext;

                    if (currentFitness >= fitness) {
                        fitness = currentFitness;
                        solSource.clear();
                        solSource.addAll(currentSolution);
                    }
                }
            }
            temperature = (temperature > 0.0001) ? (temperature * alpha) : 0.0001;
            System.out.print("\n" + (t + 1) + "\t: " + fitness);
        }
        System.out.println("\n" + "Final temperature : " + temperature);
    }


    @Override
    public List<Triple<Integer, Integer, Double>> getSolution() {
        solve();
        return enrichSolutionWithSimilarityScores();
    }

    private List<Integer> generateSuccessor(List<Integer> solSource) {
        if (solSource.isEmpty())
            return solSource;

        //int batchSz = Math.min(6, (row / 2) * 2);
        // 5% of state size -> round up (addition of 0.5) if odd then use next lower integer (this is why / 2 * 2)
        long batchSz = (Math.round(solSource.size() * 0.05 + 0.5) / 2) * 2;
        int[] randInx = random.ints(0, solSource.size()).distinct().limit(batchSz).toArray();
        List<Integer> successor = new ArrayList<>(solSource);
        for (int i = 0; i < batchSz; i += 2)
            java.util.Collections.swap(successor, randInx[i], randInx[i + 1]);

        return successor;
    }

    private double computeFitness(List<Integer> solSource) {
        var result = 0.0;
        for (int i = 0; i < solSource.size(); i++) {
            result += similarityFunction(solSource.get(i), solTarget.get(i));
        }
        return result;
    }

    private void updateFitness() {
        fitness = computeFitness(solSource);
    }

    private void randomGreedyInitTechnique() {
        List<Integer> randOrderSource = random.ints(0, row)
                .distinct()
                .limit(row)
                .boxed()
                .collect(Collectors.toList());
        List<Integer> randOrderTarget = random.ints(0, col)
                .distinct()
                .limit(col)
                .boxed()
                .collect(Collectors.toList());

        for (int i : randOrderSource) {

            List<Integer> timesI = new ArrayList<>();
            List<Integer> maxSimIndexes = new ArrayList<>();
            List<Double> maxSimScores = new ArrayList<>();
            int maxSimIndex = -1;
            double maxSim = -1;
            for (int j : randOrderTarget) {
                var similarity = similarityFunction(i, j);
                if (similarity > maxSim) {
                    maxSim = similarity;
                    maxSimIndex = j;
                }
                if (similarity >= threshold) {
                    timesI.add(i);
                    maxSimIndexes.add(j);
                    maxSimScores.add(similarityFunction(i, j));
                }
            }

            if (!maxSimScores.isEmpty()) {
                solSource.addAll(timesI);
                solTarget.addAll(maxSimIndexes);
            } else {
                //In order to keep i in the search space, we use an alignment with highest score
                solSource.add(i);
                solTarget.add(maxSimIndex);
            }
        }
    }

    private List<Triple<Integer, Integer, Double>> enrichSolutionWithSimilarityScores() {
        List<Triple<Integer, Integer, Double>> res = new ArrayList<>();
        for (int i = 0; i < solSource.size(); i++) {
            var score = similarityFunction(solSource.get(i), solTarget.get(i));
            if (score >= threshold)
                res.add(new Triple<>(solSource.get(i), solTarget.get(i), score));
        }
        return res;
    }

    private double similarityFunction(int i, int j) {
        return similarity[i][j] + similarityStructural[i][j] * 0.1 + similarityChildren[i][j] * 0.3;
    }
}
