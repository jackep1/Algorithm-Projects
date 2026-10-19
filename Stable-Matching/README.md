# Stable Matching

A Python implementation of the Gale-Shapley algorithm for the Stable Marriage Problem, with strict input validation and timing experiments.

**Course:** CSC 440 Algorithms, University of Rhode Island · **Language:** Python 3 · **Partner project** with Shina Adewumi

## Overview

The program reads preference lists for `n` knights and `n` ladies from a file and produces a stable matching: no knight and lady would both prefer each other over their assigned partners.

## Approach

Gale-Shapley with `O(n^2)` running time. The input parser enforces the file's structure and exits with an error when it is violated: wrong total line count, a person without exactly `n` preferences, a repeated preference, or an empty file.

## Testing and Benchmarks

Sample input files cover valid inputs of 10, 100, and 1000 people plus malformed cases (bad line, repeated preference, wrong `n`, too-small `n`).

| Input size (n) | Average run time |
|---|---|
| 10 | 0.000048 s |
| 100 | 0.0016 s |
| 1000 | 0.77 s |

Run time grows roughly quadratically, as the analysis predicts.

## Usage

```bash
python marriage.py marriage_inputs_10.txt
```

## Project Structure

```
marriage.py        Parser and Gale-Shapley implementation
marriage_*.txt     Valid and invalid sample inputs
Part 1 write-up    Perfect Marriage: timing and analysis
Part 2 write-up    Pandemic: written problem
```

## Credits

Written with Shina Adewumi for CSC 440. Assignment provided by the course.
