# Seam Carving

Content-aware image resizing in Python: it removes the lowest-energy path of pixels (a seam) so images shrink without distorting their important features.

**Course:** CSC 440 Algorithms, University of Rhode Island · **Language:** Python 3

## Overview

An image's energy marks how much each pixel differs from its neighbors. Seam carving repeatedly finds the vertical seam with the least total energy and deletes it.

## Approach

`best_seam` has two modes:

- **Dynamic programming (default):** fill a table of minimum cumulative energy from the bottom row up, store a backtrack pointer for each pixel (down-left, down, or down-right), then trace back from the cheapest top pixel
- **Recursive mode** (`dp=False`) for comparison

`remove_best_seam` then deletes the seam from the image.

## Usage

```bash
python gui.py    # open an image and shrink it interactively
python test_resizeable_image.py
```

## Project Structure

```
resizeable_image.py        best_seam and remove_best_seam (my implementation)
imagematrix.py, gui.py     Image class and GUI (provided by the course)
test_resizeable_image.py   Tests
```

## Credits

Starter code, image class, and GUI were provided by the course. The seam search is my work.
