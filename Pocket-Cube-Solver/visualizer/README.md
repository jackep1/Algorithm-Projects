# Pocket Cube Solver

A solver for the 2x2x2 Rubik's Cube that finds the shortest sequence of moves using a two-way breadth-first search.

**Course:** CSC 440 Algorithms, University of Rhode Island · **Language:** Python 3

## Overview

A one-directional search to the deepest positions (14 moves) needs far too much memory. Searching from both the starting position and the solved position and meeting in the middle keeps each search shallow.

## Approach

- A parity check on permutation inversions rejects unsolvable positions immediately
- Two queues and two visited maps, one growing from the start and one from the solved cube
- When the searches share a position, the two move sequences are joined into one shortest solution

## Usage

```bash
python rubik_solver_GUI.py        # Linux/macOS; on Windows run rubik_solver_GUI_Win.py
python test_solver.py
```

## Project Structure

```
solver.py                    shortest_path and helpers [confirm final version]
methods.py                   Earlier attempt(s) [confirm or remove]
rubik/                       Cube library and GUI (provided by the course)
```

## Credits

The cube library and GUI were provided by the course. The solver (solver.py) is my work.
