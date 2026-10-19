import os
import sys
import struct      # packs/unpacks the 4-byte message-length header
import marshal     # used by the provided file I/O code at the bottom
import array       # array.array('B') = compact list of unsigned bytes (0-255)
import heapq       # min-heap, used to repeatedly find the two rarest nodes
from collections import Counter   # counts how often each byte appears
try:
    import cPickle as pickle      # Python 2 name
except ImportError:
    import pickle                 # Python 3 name

# =============================================================================
# OVERVIEW
# =============================================================================
# Huffman coding gives frequent bytes SHORT bit codes and rare bytes LONG bit
# codes, so the whole message takes fewer bits than "8 bits per byte".
#
# Pipeline:
#   compress:    message -> count bytes -> build tree -> make codes
#                        -> pack codes into real bytes
#   decompress:  read tree back -> walk tree bit by bit -> original bytes
#
# code/decode are the "debug" versions: they produce a string like "0110101"
# (one character per bit) so you can read it. compress/decompress produce real
# packed bytes and are the ones that actually save space.
#
# -----------------------------------------------------------------------------
# REPRESENTATION AND INVARIANTS
# -----------------------------------------------------------------------------
# * Internally, a message is a sequence of byte VALUES (ints 0-255), not
#   characters. This makes the program work for any file, not just text.
#
# * The tree is made of Node objects:
#     - leaf node:     char is an int 0-255, left/right are None
#     - internal node: char is None, and it ALWAYS has exactly two children
#   (We test "is this a leaf?" with `char is not None`, never `if char:`,
#   because byte value 0 is a perfectly valid character but is "falsy".)
#
# * Code convention: going LEFT appends a 0 bit, going RIGHT appends a 1 bit.
#   A byte's code is the path from the root to its leaf. Because bytes only
#   live at leaves, no code is a prefix of another, so decoding is unambiguous.
#
# * The tree is saved next to the compressed data as a "decoder ring" blob:
#     [ 4 bytes: original message length n, big-endian ]
#     [ pre-order bit stream describing the tree, zero-padded to a full byte:
#         internal node -> bit 1, then left subtree, then right subtree
#         leaf          -> bit 0, then the 8 bits of its byte value ]
#   n is stored because the last compressed byte is padded with extra 0 bits;
#   without n, the decoder couldn't tell padding from real data.
# =============================================================================


class Node:
    """One node of the Huffman tree (leaf or internal; see invariants above)."""

    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq    # how many times this node's bytes occur in total
        self.char = char    # byte value (0-255) for a leaf, None for internal
        self.left = left    # child reached by a 0 bit
        self.right = right  # child reached by a 1 bit

    def __lt__(self, other):
        # heapq compares items with "<". Ordering by frequency makes the heap
        # hand back the LEAST frequent node first, which is what Huffman needs.
        return self.freq < other.freq


def _as_bytes(msg):
    """Normalize the input to a bytearray of ints 0-255.

    Callers may pass bytes (from a file), a bytearray, or a text str (like the
    assignment's example code("hello")). Iterating a bytearray gives ints in
    both Python 2 and 3, which keeps the rest of the code simple.
    """
    if isinstance(msg, (bytes, bytearray)):
        return bytearray(msg)
    # A Python 3 str (or Python 2 unicode): turn it into bytes first.
    return bytearray(msg.encode('utf-8'))


def build_tree(char_counts):
    """Build the Huffman tree from a {byte value: count} dictionary.

    Greedy algorithm: repeatedly take the two least frequent nodes and join
    them under a new parent whose frequency is their sum. Cost is
    O(k log k) for k distinct bytes, because each heap operation is O(log k).
    Returns the root Node, or None if there is nothing to encode.
    """
    # Start with one leaf per distinct byte.
    heap = [Node(freq, char) for char, freq in char_counts.items()]

    # Empty message: no symbols, so no tree.
    if not heap:
        return None

    # Only one distinct byte: a lone leaf would have a ZERO-length code (no
    # path from root to itself) and decoding would try to step off the tree.
    # Fix: make an internal root with the real leaf on the left (code "0")
    # and a dummy leaf on the right that never actually gets used.
    if len(heap) == 1:
        leaf = heap[0]
        return Node(leaf.freq, None, leaf, Node(0, leaf.char))

    # Rearrange the list in place so heap[0] is always the smallest node.
    heapq.heapify(heap)

    # Each pass removes two nodes and adds one, so the heap shrinks by one.
    # We stop when a single node (the root) remains.
    while len(heap) > 1:
        left = heapq.heappop(heap)    # rarest node
        right = heapq.heappop(heap)   # second rarest
        # The new parent isn't a character, so char=None (internal node).
        heapq.heappush(heap, Node(left.freq + right.freq, None, left, right))

    return heap[0]


def tree_to_binary(root, n):
    """Serialize the tree plus the message length n into bytes.

    Format is described at the top of the file. A recursive pre-order walk
    emits 1 for each internal node and 0 + 8 bits for each leaf, so the reader
    can rebuild the exact same tree without being told how big it is.
    """
    # We collect individual bits in a plain list (the tree is tiny: at most
    # 256 leaves + 255 internal nodes) and pack them into bytes at the end.
    bits = []

    def walk(node):
        if node.char is not None:          # leaf (NOT `if node.char:` - see top)
            bits.append(0)                 # 0 = "leaf follows"
            # Append the byte value as 8 bits, most significant bit first.
            # (value >> i) & 1 extracts bit number i (counting from the right).
            bits.extend((node.char >> i) & 1 for i in range(7, -1, -1))
        else:
            bits.append(1)                 # 1 = "internal node"
            walk(node.left)                # then its two subtrees, in order
            walk(node.right)

    if root is not None:
        walk(root)

    # Pad with zeros so the bit count is a multiple of 8 (whole bytes only).
    # The reader never looks at these: the structure itself says when the
    # tree ends.
    while len(bits) % 8:
        bits.append(0)

    # Header: the message length as a 4-byte big-endian unsigned int ('>I').
    out = bytearray(struct.pack('>I', n))

    # Pack each group of 8 bits into one byte.
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i + 8]:
            byte = (byte << 1) | b         # shift left, then append bit b
        out.append(byte)

    return bytes(out)


def binary_to_tree(data):
    """Inverse of tree_to_binary. Returns (root Node, message length n)."""
    data = bytearray(data)    # indexing gives ints in both Python 2 and 3

    # First 4 bytes are the message length header.
    n = struct.unpack('>I', bytes(data[:4]))[0]
    if n == 0:                # empty message: there is no tree to read
        return None, 0

    # Current position in the bit stream, in BITS. A one-element list lets the
    # nested functions modify it (Python 2 has no `nonlocal`). We start at bit
    # 32 because the first 4 bytes (32 bits) are the header.
    pos = [32]

    def read_bit():
        p = pos[0]
        pos[0] += 1
        # p // 8 picks the byte, p % 8 the bit within it. Bits are stored
        # from the left (most significant) end, so bit 0 of a byte is
        # shifted right by 7, bit 1 by 6, and so on. `& 1` isolates it.
        return (data[p // 8] >> (7 - p % 8)) & 1

    def read_node():
        if read_bit() == 0:           # 0 = leaf: next 8 bits are its byte value
            c = 0
            for _ in range(8):
                c = (c << 1) | read_bit()   # rebuild the value bit by bit
            # freq isn't needed for decoding, so it's just set to 0.
            return Node(0, c)
        # 1 = internal node: it's followed by its left subtree, then right.
        # The order of these two lines MUST match the order in walk() above.
        left = read_node()
        right = read_node()
        return Node(0, None, left, right)

    return read_node(), n


def _make_codes(root):
    """Walk the tree and return {byte value: (code as an int, code length)}.

    The code is kept as an int plus a length (not a "0101" string) so that
    compress() can pack it with fast shifts. The length is needed because
    leading zeros vanish in an int: code 001 and code 1 are both the number 1.
    """
    codes = {}

    def gen(node, value, length):
        if node.char is not None:                   # reached a leaf: record it
            codes[node.char] = (value, length)
            return
        # Going left appends a 0 bit: shift the code left, new bit is 0.
        gen(node.left, value << 1, length + 1)
        # Going right appends a 1 bit: shift left, then set the lowest bit.
        gen(node.right, (value << 1) | 1, length + 1)

    if root is not None:
        gen(root, 0, 0)
    return codes


def code(message):
    """Human-readable encoding: returns (string of '0'/'1' chars, tree blob).

    This does NOT save space (one character per bit); it exists so you can
    inspect the result and check your logic before doing the bit packing.
    """
    msg = _as_bytes(message)
    root = build_tree(Counter(msg))     # Counter: {byte value: occurrences}
    codes = _make_codes(root)

    pieces = []
    for b in msg:
        v, l = codes[b]
        # format(v, '05b') writes v in binary padded with leading zeros to
        # width 5. Padding to the code length restores any leading 0s that
        # the int representation dropped (e.g. code 001 -> "001", not "1").
        pieces.append(format(v, '0%db' % l))
    return ''.join(pieces), tree_to_binary(root, len(msg))


def decode(message, decoderRing):
    """Inverse of code(): '0'/'1' string + tree blob -> original bytes."""
    root, n = binary_to_tree(decoderRing)
    out = bytearray()
    node = root                          # start every symbol at the root
    for bit in message:
        if len(out) == n:                # got everything; ignore any leftovers
            break
        # Follow the path: '0' goes left, anything else ('1') goes right.
        node = node.left if bit == '0' else node.right
        if node.char is not None:        # hit a leaf: one symbol is complete
            out.append(node.char)
            node = root                  # go back to the top for the next one
    return bytes(out)


def compress(message):
    """Real compression: returns (array of packed bytes, tree blob)."""
    msg = _as_bytes(message)
    root = build_tree(Counter(msg))
    codes = _make_codes(root)

    compressed = array.array('B')   # 'B' = unsigned byte, values 0-255

    # `buf` holds bits that have been added but not yet written out, and
    # `nbits` says how many of buf's low bits are valid.
    buf = 0
    nbits = 0
    for b in msg:
        v, l = codes[b]
        buf = (buf << l) | v        # append this byte's l-bit code to buf
        nbits += l
        # Whenever at least 8 bits are waiting, write the oldest 8 as a byte.
        while nbits >= 8:
            nbits -= 8
            # Shift right so the oldest complete group of 8 bits is at the
            # bottom, then mask with 0xFF (binary 11111111) to keep only it.
            compressed.append((buf >> nbits) & 0xFF)
        # Throw away the bits we just wrote, keeping only the `nbits` leftover
        # low bits. (1 << nbits) - 1 is a mask of nbits ones. Without this,
        # buf would grow without bound on a big file and get very slow.
        buf &= (1 << nbits) - 1

    # Fewer than 8 bits may be left over. Shift them to the TOP of a final
    # byte; the unused low bits become zero padding. decompress() ignores the
    # padding because it stops after n symbols.
    if nbits:
        compressed.append((buf << (8 - nbits)) & 0xFF)

    return compressed, tree_to_binary(root, len(msg))


def decompress(message, decoderRing):
    """Inverse of compress(): packed bytes + tree blob -> original bytes."""
    root, n = binary_to_tree(decoderRing)
    out = bytearray()
    node = root
    for byte in bytearray(message):      # iterating a bytearray gives ints
        if len(out) == n:                # done; the rest is just padding
            break
        # Read the 8 bits of this byte from the top (bit 7) down to bit 0,
        # which is the same order compress() wrote them.
        for i in range(7, -1, -1):
            # (byte >> i) & 1 is the value of bit i: 0 -> left, 1 -> right.
            node = node.right if (byte >> i) & 1 else node.left
            if node.char is not None:    # reached a leaf: output its byte
                out.append(node.char)
                node = root              # restart at the top for the next one
                # The last byte may have padding bits. Stop as soon as we have
                # all n symbols so those bits aren't decoded as extra data.
                if len(out) == n:
                    break
    return bytes(out)


def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            compr, tree = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), compr), fcompressed)
            fcompressed.close()
        else:
            enc, tree = code(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        tree = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, tree)
        else:
            msg = decode(compr, tree)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close()