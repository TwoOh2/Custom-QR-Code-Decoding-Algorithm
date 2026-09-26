import numpy as np

def calculate_penalty_rule_1(matrix):
    penalty = 0
    size = matrix.shape[0]
    for r in range(size):
        for c in range(size - 4):
            if np.all(matrix[r, c:c+5] == matrix[r, c]):
                penalty += 3
    for c in range(size):
        for r in range(size - 4):
            if np.all(matrix[r:r+5, c] == matrix[r, c]):
                penalty += 3
    return penalty

def calculate_penalty_rule_2(matrix):
    penalty = 0
    size = matrix.shape[0]
    for r in range(size - 1):
        for c in range(size - 1):
            if matrix[r, c] == matrix[r, c+1] == matrix[r+1, c] == matrix[r+1, c+1]:
                penalty += 3
    return penalty

def apply_unmask(matrix, mask_pattern=0):
    size = matrix.shape[0]
    unmasked = np.copy(matrix)
    for r in range(size):
        for c in range(size):
            if mask_pattern == 0:
                condition = (r + c) % 2 == 0
            elif mask_pattern == 1:
                condition = r % 2 == 0
            elif mask_pattern == 2:
                condition = c % 3 == 0
            elif mask_pattern == 3:
                condition = (r + c) % 3 == 0
            elif mask_pattern == 4:
                condition = (r // 2 + c // 3) % 2 == 0
            elif mask_pattern == 5:
                condition = ((r * c) % 2) + ((r * c) % 3) == 0
            elif mask_pattern == 6:
                condition = (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
            elif mask_pattern == 7:
                condition = (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
            else:
                condition = False
            
            if condition:
                unmasked[r, c] ^= 1
    return unmasked