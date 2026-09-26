import numpy as np

def is_function_module(r, c, size):
    if (r < 9 and c < 9) or (r < 9 and c >= size - 8) or (r >= size - 8 and c < 9):
        return True
    if r == 6 or c == 6:
        return True
    if size > 21:
        align_center = {25: 18, 29: 22, 33: 26}[size]
        if align_center - 2 <= r <= align_center + 2 and align_center - 2 <= c <= align_center + 2:
            return True
    return False

def extract_bits(matrix):
    size = matrix.shape[0]
    bits = []
    col = size - 1
    row = size - 1
    upward = True
    while col > 0:
        if col == 6:
            col -= 1
            continue
        for i in range(size):
            r = row - i if upward else i
            for c in (col, col - 1):
                if not is_function_module(r, c, size):
                    bits.append(matrix[r, c])
        upward = not upward
        col -= 2
    return bits
