package org.baseline;

import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.AlignmentSerializer;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.rdf.model.ModelFactory;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.net.URI;
import java.net.URISyntaxException;

public class Main {
    public static void main(String[] args) throws Exception {
        URI sourceUri = null;
        URI targetUri = null;
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


        var matcher = new BaselineMatcher();
        var alignment = matcher.match(source, target, null, null);
        AlignmentSerializer.serialize(alignment, new File(outputFile));
    }
}