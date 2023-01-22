package org.evolutionary_algorithm;

import java.net.URL;
import java.util.List;

public class OntoClazz {

    private final Integer internalId;
    private final String uri;
    private final List<String> labels;
    private final List<String> comments;

    OntoClazz(Integer internalId, String uri, List<String> labels, List<String> comments) {
        this.internalId = internalId;
        this.uri = uri;
        this.labels = labels;
        this.comments = comments;
    }

    public Integer getInternalId() {
        return internalId;
    }

    public String getId() {
        var uriParts = uri.split("/");
        return uriParts[uriParts.length - 1];
    }

    public String getUri() {
        return uri;
    }

    public List<String> getLabels() {
        return labels;
    }

    public List<String> getComments() {
        return comments;
    }
}
