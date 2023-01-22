package org.sanom.matcher;

import org.sanom.util.Triple;
import org.sanom.util.Tuple;

import java.util.List;

public interface IAlignmentMethod {

    List<Triple<Integer, Integer, Double>> getSolution();
}
