import numpy as np

# Precomputed XORed format strings for all 32 combinations (ECC + Mask)
FORMAT_INFO_TABLE = {
    (1, 0): 0x77C4, (1, 1): 0x72F3, (1, 2): 0x7DAA, (1, 3): 0x789D,
    (1, 4): 0x662F, (1, 5): 0x6318, (1, 6): 0x6C41, (1, 7): 0x6976,
    (0, 0): 0x5412, (0, 1): 0x5125, (0, 2): 0x5E7C, (0, 3): 0x5B4B,
    (0, 4): 0x45F9, (0, 5): 0x40CE, (0, 6): 0x4F97, (0, 7): 0x4AA0,
    (3, 0): 0x355F, (3, 1): 0x3068, (3, 2): 0x3F31, (3, 3): 0x3A06,
    (3, 4): 0x24B4, (3, 5): 0x2183, (3, 6): 0x2EDA, (3, 7): 0x2BED,
    (2, 0): 0x1689, (2, 1): 0x13BE, (2, 2): 0x1CE7, (2, 3): 0x19D0,
    (2, 4): 0x0762, (2, 5): 0x0255, (2, 6): 0x0D0C, (2, 7): 0x083B
}

def hamming_weight(x):
    return bin(x).count("1")

def decode_format_info(matrix):
    size = matrix.shape[0]
    
    # Read primary format info (top-left)
    bits = []
    for c in range(6): bits.append(matrix[8, c])
    bits.append(matrix[8, 7])
    bits.append(matrix[8, 8])
    bits.append(matrix[7, 8])
    for r in range(5, -1, -1): bits.append(matrix[r, 8])
    
    format_val1 = int(''.join(str(b) for b in bits), 2)
    
    # Read secondary format info (top-right and bottom-left)
    bits2 = []
    for r in range(size - 1, size - 8, -1): bits2.append(matrix[r, 8])
    for c in range(size - 8, size): bits2.append(matrix[8, c])
    
    format_val2 = int(''.join(str(b) for b in bits2), 2)
    
    # Find best match using Hamming distance
    best_dist = 15
    best_ecc = 1
    best_mask = 0
    
    for (ecc, mask), expected_val in FORMAT_INFO_TABLE.items():
        dist1 = hamming_weight(format_val1 ^ expected_val)
        dist2 = hamming_weight(format_val2 ^ expected_val)
        if dist1 < best_dist:
            best_dist = dist1
            best_ecc = ecc
            best_mask = mask
        if dist2 < best_dist:
            best_dist = dist2
            best_ecc = ecc
            best_mask = mask
            
    if best_dist <= 3:
        return best_ecc, best_mask
    return 1, 0 # Default to L, Mask 0 on catastrophic failure
