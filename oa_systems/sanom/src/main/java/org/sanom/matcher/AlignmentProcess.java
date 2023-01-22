package org.sanom.matcher;

import fr.inrialpes.exmo.align.impl.DistanceAlignment;
import fr.inrialpes.exmo.ontowrap.HeavyLoadedOntology;
import fr.inrialpes.exmo.ontowrap.OntologyFactory;
import fr.inrialpes.exmo.ontowrap.OntowrapException;
import org.sanom.preprocessing.Preprocessor;
import org.sanom.similarity.SimilarityMetric;
import org.semanticweb.owl.align.AlignmentException;
import org.semanticweb.owlapi.model.*;
import uk.ac.manchester.cs.owl.owlapi.OWLClassImpl;

import java.io.*;
import java.net.URI;
import java.util.*;
import java.util.function.Supplier;

public class AlignmentProcess extends DistanceAlignment implements org.semanticweb.owl.align.AlignmentProcess {

    private final HeavyLoadedOntology<Object> heavyOntology1;
    private final HeavyLoadedOntology<Object> heavyOntology2;

    public AlignmentProcess(URI source, URI target) throws AlignmentException, OntowrapException {
        super.init(source, target);
        setType("**");

        OntologyFactory.setDefaultFactory("fr.inrialpes.exmo.ontowrap.owlapi30.OWLAPI3OntologyFactory");
        heavyOntology1 = (HeavyLoadedOntology<Object>) OntologyFactory.getFactory().loadOntology(source);
        heavyOntology2 = (HeavyLoadedOntology<Object>) OntologyFactory.getFactory().loadOntology(target);
    }

    public SimilarityMatrices getSimilarityMatrices(
            Preprocessor preprocessor,
            SimilarityMetric similarityMetric,
            String filename
    ) throws OntowrapException, IOException {

        File file = new File(filename);
        if (file.exists()) {
            System.out.println("Found existing similarity matrix file -> skip computation");
            return readFromFile(file);
        }

        int nbEntities1 = heavyOntology1.nbClasses();
        int nbEntities2 = heavyOntology2.nbClasses();
        OWLObject[] entity1o = heavyOntology1.getClasses().toArray(new OWLObject[nbEntities1]);
        OWLObject[] entity2o = heavyOntology2.getClasses().toArray(new OWLObject[nbEntities2]);


        //initializing the list of lexicons
        List<List<String>> entity1ss = new ArrayList<>(nbEntities1);
        List<List<String>> entity2ss = new ArrayList<>(nbEntities1);

        for (OWLObject ob : entity1o) {
            List<String> names = new ArrayList<>();
            for (OWLAnnotationAssertionAxiom ob1 : ((OWLOntology) heavyOntology1.getOntology()).getAnnotationAssertionAxioms(((OWLClass) ob).getIRI())) {
                if (ob1.getProperty().isLabel()) {
                    names.addAll(preprocessor.getBagOfWords(
                            ((OWLLiteral) ob1.getValue()).getLiteral())
                    );
                } else if (ob1.getProperty().toStringID().endsWith("hasRelatedSynonym")) {
                    names.addAll(preprocessor.getBagOfWords(
                            ((OWLLiteral) (((OWLOntology) heavyOntology1.getOntology()).getAnnotationAssertionAxioms((OWLAnnotationSubject) ob1.getValue()).iterator().next()).getValue()).getLiteral()
                    ));
                }
            }
            //If no labels and hasRelatedSynonym are present, then use the iri as name
            if (names.size() <= 0) {
                names.addAll(
                        preprocessor.getBagOfWords(ob.getClassesInSignature().iterator().next().getIRI().getFragment())
                );
            }
            entity1ss.add(names);
        }

        for (OWLObject ob : entity2o) {
            List<String> names = new ArrayList<>();
            for (OWLAnnotationAssertionAxiom ob1 : ((OWLOntology) heavyOntology2.getOntology()).getAnnotationAssertionAxioms(((OWLClass) ob).getIRI())) {
                if (ob1.getProperty().isLabel()) {
                    names.addAll(
                            preprocessor.getBagOfWords(((OWLLiteral) ob1.getValue()).getLiteral())
                    );
                } else if (ob1.getProperty().toStringID().endsWith("hasRelatedSynonym")) {
                    names.addAll(
                            preprocessor.getBagOfWords(((OWLLiteral) (((OWLOntology) heavyOntology2.getOntology()).getAnnotationAssertionAxioms((OWLAnnotationSubject) ob1.getValue()).iterator().next()).getValue()).getLiteral())
                    );
                }
            }
            //If no labels and hasRelatedSynonym are present, then use the iri as name
            if (names.size() <= 0) {
                names.addAll(
                        preprocessor.getBagOfWords(ob.getClassesInSignature().iterator().next().getIRI().getFragment())
                );
            }
            entity2ss.add(names);
        }

        similarityMetric.init(entity1ss, entity2ss);

        System.out.println("Computing similarity matrix...");

        int i, j;
        double progressTrackerStep = 100.0 / nbEntities1;
        double progressTracker = progressTrackerStep;

        // Compute similarity value from each concept of the source ontology to each concept in the target ontology
        double[][] matrix = new double[nbEntities1][nbEntities2];
        for (i = 0; i < nbEntities1; i++, progressTracker += progressTrackerStep) {
            for (j = 0; j < nbEntities2; j++) {
                matrix[i][j] = similarityMetric.getSimilarityMetric(entity1ss.get(i), entity2ss.get(j));
            }
            System.out.printf("\r%.0f%% completed!", progressTracker);
        }

        //Create sup01 and sup02 that contain for each class all the super classes
        List<Set<String>> supO1 = new ArrayList<>();
        List<Set<String>> supO2 = new ArrayList<>();
        List<Set<String>> subO1 = new ArrayList<>();
        List<Set<String>> subO2 = new ArrayList<>();
        Map<String, Set<String>> subClassMap1 = new HashMap<>();
        Map<String, Set<String>> subClassMap2 = new HashMap<>();
        double[][] matSup = new double[nbEntities1][nbEntities2];
        double[][] matSub = new double[nbEntities1][nbEntities2];
        HashMap<String, Integer> iriC1 = new HashMap<>(nbEntities1);
        HashMap<String, Integer> iriC2 = new HashMap<>(nbEntities2);
        String iri;

        for (i = 0; i < nbEntities1; i++) {
            var currentIri = ((OWLClass) entity1o[i]).getIRI().toString();
            iriC1.put(currentIri, i);
            Set<String> temp = new HashSet<>();
            for (OWLObject ob : ((OWLClassImpl) entity1o[i]).getSuperClasses((OWLOntology) heavyOntology1.getOntology())) {
                if (ob.getClass().toString().startsWith("class")) {
                    iri = ob.getClassesInSignature().iterator().next().getIRI().toString();
                    if (!iri.endsWith("Thing")) {
                        temp.add(iri);
                        subClassMap1.putIfAbsent(iri, new HashSet<>());
                        subClassMap1.get(iri).add(currentIri);
                    }
                }
            }
            supO1.add(temp);
        }

        for (i = 0; i < nbEntities1; i++) {
            var currentIri = ((OWLClass) entity1o[i]).getIRI().toString();
            subO1.add(subClassMap1.getOrDefault(currentIri, new HashSet<>()));
        }

        for (i = 0; i < nbEntities2; i++) {
            var currentIri = ((OWLClass) entity2o[i]).getIRI().toString();
            iriC2.put(currentIri, i);
            Set<String> temp = new HashSet<>();
            for (OWLObject ob : ((OWLClassImpl) entity2o[i]).getSuperClasses((OWLOntology) heavyOntology2.getOntology())) {
                if (ob.getClass().toString().startsWith("class")) {
                    iri = ob.getClassesInSignature().iterator().next().getIRI().toString();
                    if (!iri.endsWith("Thing")) {
                        temp.add(iri);
                        subClassMap2.putIfAbsent(iri, new HashSet<>());
                        subClassMap2.get(iri).add(currentIri);
                    }
                }
            }
            supO2.add(temp);
        }

        for (i = 0; i < nbEntities2; i++) {
            var currentIri = ((OWLClass) entity2o[i]).getIRI().toString();
            subO2.add(subClassMap2.getOrDefault(currentIri, new HashSet<>()));
        }

        // The next loop computes the structural similarity score, i.e. it computes the maximum similarity score that two classes' parents share
        double maxSim;
        for (i = 0; i < nbEntities1; i++) {
            for (j = 0; j < nbEntities2; j++) {
                maxSim = 0.0;
                for (String ob1 : supO1.get(i)) {
                    int ind1 = iriC1.get(ob1);
                    for (String ob2 : supO2.get(j))
                        maxSim = Math.max(maxSim, matrix[ind1][iriC2.get(ob2)]);
                }
                matSup[i][j] = maxSim;
                maxSim = 0.0;
                for (String ob1 : subO1.get(i)) {
                    int ind1 = iriC1.get(ob1);
                    for (String ob2 : subO2.get(j)) {
                        maxSim = Math.max(maxSim, matrix[ind1][iriC2.get(ob2)]);
                    }
                }
                matSub[i][j] = maxSim;
            }
        }

        var similarityMatrices = new SimilarityMatrices(matrix, matSup, matSub);

        writeToFile(similarityMatrices, file);

        return similarityMatrices;
    }

    private void writeToFile(SimilarityMatrices similarityMatrices, File file) throws IOException {
        System.out.println("Write to file....");
        file.getParentFile().mkdirs();

        FileWriter fileWriter = new FileWriter(file);
        PrintWriter printWriter = new PrintWriter(fileWriter);

        printWriter.println("--Similarity--");
        for (int i = 0; i < similarityMatrices.getSimilarity().length; i++) {
            printWriter.println(Arrays.stream(similarityMatrices.getSimilarity()[i]).mapToObj(String::valueOf).reduce((s, s2) -> s + " " + s2).get());
        }

        printWriter.println("--Sup--");
        for (int i = 0; i < similarityMatrices.getSupSimilarity().length; i++) {
            printWriter.println(Arrays.stream(similarityMatrices.getSupSimilarity()[i]).mapToObj(String::valueOf).reduce((s, s2) -> s + " " + s2).get());
        }

        printWriter.println("--Sub--");
        for (int i = 0; i < similarityMatrices.getSubSimilarity().length; i++) {
            printWriter.println(Arrays.stream(similarityMatrices.getSubSimilarity()[i]).mapToObj(String::valueOf).reduce((s, s2) -> s + " " + s2).get());
        }

        printWriter.close();
    }

    private SimilarityMatrices readFromFile(File file) throws FileNotFoundException {
        FileInputStream fis = new FileInputStream(file);
        Scanner sc = new Scanner(fis);

        boolean isReadingSimilarityMatrix = false;
        boolean isReadingSupMatrix = false;
        boolean isReadingSubMatrix = false;
        List<double[]> similarityMatrix = new ArrayList<>();
        List<double[]> supMatrix = new ArrayList<>();
        List<double[]> subMatrix = new ArrayList<>();

        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            if (line.equals("--Similarity--")) {
                isReadingSimilarityMatrix = true;
                isReadingSupMatrix = false;
                isReadingSubMatrix = false;
            } else if (line.equals("--Sup--")) {
                isReadingSupMatrix = true;
                isReadingSimilarityMatrix = false;
                isReadingSubMatrix = false;
            } else if (line.equals("--Sub--")) {
                isReadingSubMatrix = true;
                isReadingSupMatrix = false;
                isReadingSimilarityMatrix = false;
            } else if (isReadingSimilarityMatrix) {
                double[] dLine = Arrays.stream(line.split(" ")).mapToDouble(Double::parseDouble).toArray();
                similarityMatrix.add(dLine);
            } else if (isReadingSupMatrix) {
                double[] dLine = Arrays.stream(line.split(" ")).mapToDouble(Double::parseDouble).toArray();
                supMatrix.add(dLine);
            } else if (isReadingSubMatrix) {
                double[] dLine = Arrays.stream(line.split(" ")).mapToDouble(Double::parseDouble).toArray();
                subMatrix.add(dLine);
            }
        }

        double[][] dSimilarityMatrix = new double[similarityMatrix.size()][similarityMatrix.get(0).length];
        for (int i = 0; i < similarityMatrix.size(); i++) {
            dSimilarityMatrix[i] = similarityMatrix.get(i);
        }
        double[][] dSupMatrix = new double[supMatrix.size()][supMatrix.get(0).length];
        for (int i = 0; i < supMatrix.size(); i++) {
            dSupMatrix[i] = supMatrix.get(i);
        }
        double[][] dSubMatrix = new double[subMatrix.size()][subMatrix.get(0).length];
        for (int i = 0; i < subMatrix.size(); i++) {
            dSubMatrix[i] = subMatrix.get(i);
        }
        sc.close();

        return new SimilarityMatrices(dSimilarityMatrix, dSupMatrix, dSubMatrix);
    }

    public void computeAlignment(
            Supplier<IAlignmentMethod> alignmentMethodSupplier
    ) throws OntowrapException, AlignmentException {

        int nbEntities1 = heavyOntology1.nbClasses();
        int nbEntities2 = heavyOntology2.nbClasses();
        OWLObject[] entity1o = heavyOntology1.getClasses().toArray(new OWLObject[nbEntities1]);
        OWLObject[] entity2o = heavyOntology2.getClasses().toArray(new OWLObject[nbEntities2]);

        IAlignmentMethod alignmentMethod = alignmentMethodSupplier.get();
        System.out.println("\nRunning: " + alignmentMethod.getClass().getSimpleName());
        var result = alignmentMethod.getSolution();
        System.out.println("\nAlignment approach finished.");
        for (var item : result)
            addAlignCell(entity1o[item.getT1()], entity2o[item.getT2()], "=", Math.min(item.getT3(), 1));

    }
}
