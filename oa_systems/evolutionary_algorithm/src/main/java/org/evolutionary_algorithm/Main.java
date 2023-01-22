package org.evolutionary_algorithm;

import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.AlignmentParser;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.AlignmentSerializer;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.rdf.model.ModelFactory;

import java.io.File;
import java.io.FileInputStream;
import java.net.URI;
import java.util.Properties;

/*
 * Differences when copared to the paper:
 *  - no smoa
 *  - no SimRank - in the paper the authors stated that it did not show to be beneficial
 *  - for mutation a custom approach is chosen since, the paper is not very specific
 *  - use weights directly, instead of segmentation points - simplifies the code
 *  - cross over operator different
 */

/*
 * Observations:
 *  - adding more similarity measures did not increase performance
 */
public class Main {
    public static void main(String[] args) throws Exception {
        URI sourceUri = null;
        URI targetUri = null;
        String referenceFile = null;
        String outputFile = null;

        for (int i = 0; i < args.length; i += 2) {
            switch (args[i]) {
                case "--source":
                    sourceUri = new URI("file:" + args[i + 1]);
                    break;
                case "--target":
                    targetUri = new URI("file:" + args[i + 1]);
                    break;
                case "--output":
                    outputFile = args[i + 1];
                    break;
                case "--reference":
                    referenceFile = args[i + 1];
            }
        }

        if (sourceUri == null || targetUri == null || outputFile == null) {
            System.out.println("Mandatory arguments are --source and --target and --output; aborting...");
            return;
        }

        OntModel source = ModelFactory.createOntologyModel();
        source.read(new FileInputStream(sourceUri.getPath()), "RDF/XML");

        OntModel target = ModelFactory.createOntologyModel();
        target.read(new FileInputStream(targetUri.getPath()), "RDF/XML");


        var matcher = new EvolutionaryAlgorithmMatcher();
        var alignment = matcher.match(source, target, null, new Properties());
        AlignmentSerializer.serialize(alignment, new File(outputFile));

        if (referenceFile != null) {
            System.out.println();
            System.out.println("Perform evaluation...");
            // eval
            Alignment ref = AlignmentParser.parse("file:" + referenceFile);
            var tp =  alignment.stream().filter(ref::contains).count();
            var precision = (double) tp / alignment.size();
            var recall = (double) tp / ref.size();
            System.out.println("Precision:");
            System.out.println("\t" + precision);
            System.out.println("Recall:");
            System.out.println("\t" + recall);
            System.out.println("F1:");
            System.out.println("\t" + 2 * precision * recall / (precision + recall));

        }

    }
}