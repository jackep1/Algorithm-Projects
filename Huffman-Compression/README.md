# Huffman Compression

A Python implementation of lossless Huffman compression and decompression for any file.

**Course:** CSC 440 Algorithms, University of Rhode Island · **Language:** Python 3

## Overview

Huffman coding assigns shorter bit strings to more frequent bytes, so the total number of bits is smaller than the usual 8 per byte. The program builds a Huffman tree from byte frequencies using a priority queue, encodes the data, and stores the tree alongside it so the file can be restored exactly.

The tree gives a prefix-free code: each byte sits at a leaf, and its code is the path from the root (left = `0`, right = `1`). Because no code is a prefix of another, decoding is unambiguous.

## Approach

- `build_tree` creates the tree from byte counts with a min-heap: repeatedly merge the two least frequent nodes into a parent until one root remains
- `code` and `decode` convert between messages and strings of 0s and 1s, which is readable but doesn't save space
- `compress` and `decompress` pack the codes into real bytes using bit shifts and masks, and unpack them again
- `tree_to_binary` and `binary_to_tree` serialize the tree so it can be saved with the data

## How It Works

1. **Count.** `Counter` tallies how often each byte value appears.
2. **Build the tree.** Start with one leaf per distinct byte in a min-heap, then merge the two rarest nodes repeatedly.
3. **Make codes.** Walk the tree once, recording each leaf's path as `{byte: (code, length)}`.
4. **Pack.** Append each code's bits to a buffer and write a byte whenever 8 bits are waiting. The last byte is zero-padded.
5. **Decode.** Rebuild the tree from the saved blob, read bits from the top of each byte, and go left on `0` and right on `1`. At a leaf, output its byte and return to the root. Stop after the original length so the padding is ignored.

## Data Structures

- **Min-heap (`heapq`)** for building the tree, since each step needs the two smallest nodes and a heap finds them in O(log k)
- **`Node` objects** for the tree: leaves hold a byte value, internal nodes hold two children
- **Dictionary** `{byte: (code, length)}` for constant-time lookups while encoding
- **`array.array('B')`** for the packed output

## Complexity

For a message of `n` bytes with `k` distinct byte values (`k <= 256`):

| Step | Cost |
|---|---|
| Counting | O(n) |
| Building the tree | O(k log k) |
| Encoding / packing | O(n) |
| Decoding | O(n) |

## Usage

```bash
python huffman.py -c input.txt output.huf     # compress
python huffman.py -d output.huf restored.txt  # decompress
python huffman.py -v input.txt codes.huf      # encode to a string of 0s and 1s (debug)
python huffman.py -w codes.huf decoded.txt    # decode that string
```

`-v` and `-w` use `code` and `decode`. The `-v` output file stores the tree and the 0/1 string together in the same container format as `-c`, so it isn't a plain text file.

## Project Structure

```
huffman.py        Implementation and command-line interface
*.txt, *.huf      Sample inputs and compressed files
```

## Credits

Assignment and function stubs were provided by the course. The implementation is my work.