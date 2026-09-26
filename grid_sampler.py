import numpy as np

def sample_grid(img, size):
    module = 10
    matrix = np.zeros((size, size), dtype=int)
    for r in range(size):
        for c in range(size):
            cell = img[r*module:(r+1)*module, c*module:(c+1)*module]
            matrix[r, c] = 1 if np.mean(cell) < 128 else 0
    return matrix
