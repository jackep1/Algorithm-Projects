# Convex Hull

A divide-and-conquer convex hull algorithm in Python, benchmarked against a naive approach.

**Course:** CSC 440 Algorithms, University of Rhode Island · **Language:** Python 3

## Overview

Given a set of 2D points, `compute_hull` returns only the points on the convex hull, in clockwise order. Points are `(x, y)` integer tuples with the origin at the upper left, as in screen coordinates (positive x-direction rightwards, positive y-direction downwards).

## Approach

1. Sort the points by x-coordinate.
2. Handle sets of five or fewer points directly with a base-case hull. The base_case_hull() function uses an algorithm which checks every single pair of points to determine if the line between them forms a boundary of the hull, leading to runtime O(n<sup>3</sup>).
3. For larger sets of points:
    1. Split the points in half recursively until small enough for the base case.
    2. Compute each half's hull recursively.
    3. Combine them with `merge_hulls` by determining the upper and lower tangents of the combined hulls (a line from a point on one hull to a point on the other which puts all other points below or above the line respectively).

Helper functions test orientation (clockwise, counter-clockwise, collinear) and compute triangle areas.

## Testing and Benchmarks

- `tests.py` checks the hull against known inputs.
- `benchmarks.py` times the divide-and-conquer hull against the base-case approach on inputs of increasing size and plots the results with `matplotlib`.
- `Benchmark.pdf` is the written analysis of the results.

## Usage

```bash
python draw_hull.py     # click to add points, then compute and draw the hull
python tests.py
python benchmarks.py
```

## Project Structure

```
convex_hull.py    compute_hull, merge_hulls, and helpers
tests.py          Unit tests
benchmarks.py     Timing experiments and plots
draw_hull.py      GUI visualizer (provided by the course)
Benchmark.pdf     Benchmark write-up
```

## Credits

Assignment, starter code, and the GUI were provided by the course. The hull algorithm (base_case_hull, compute_hull, and merge_hulls functions) and benchmarks are my work.
