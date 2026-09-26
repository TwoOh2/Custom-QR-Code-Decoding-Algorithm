import numpy as np


EXP_TABLE = np.zeros(512, dtype=int)
LOG_TABLE = np.zeros(256, dtype=int)

def init_gf():
    x = 1
    for i in range(255):
        EXP_TABLE[i] = x
        LOG_TABLE[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11d
    for i in range(255, 512):
        EXP_TABLE[i] = EXP_TABLE[i - 255]

init_gf()

def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[LOG_TABLE[a] + LOG_TABLE[b]]

def gf_pow(a, power):
    return EXP_TABLE[(LOG_TABLE[a] * power) % 255]

def gf_inverse(a):
    return EXP_TABLE[255 - LOG_TABLE[a]]



def generate_generator_poly(ecc_len=7):
    g = [1]
    for i in range(ecc_len):
        g = poly_mul(g, [1, gf_pow(2, i)])
    return g

def poly_mul(p1, p2):
    res = [0] * (len(p1) + len(p2) - 1)
    for i, a in enumerate(p1):
        for j, b in enumerate(p2):
            res[i + j] ^= gf_mul(a, b)
    return res

def poly_mod(dividend, divisor):
    result = dividend[:]
    while len(result) >= len(divisor):
        coef = result[0]
        if coef != 0:
            for i in range(len(divisor)):
                result[i] ^= gf_mul(divisor[i], coef)
        result = result[1:]
    return result



def berlekamp_massey(syndromes):
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
    for i in range(len(syndromes)):
        d = syndromes[i]
        for j in range(1, L + 1):
            if j < len(C) and i - j >= 0:
                d ^= gf_mul(C[j], syndromes[i - j])
        if d == 0:
            m += 1
        else:
            T = C[:]
            factor = gf_mul(d, gf_inverse(b))
            scaled_B = [0] * m + [gf_mul(factor, x) for x in B]
            max_len = max(len(C), len(scaled_B))
            C = C + [0] * (max_len - len(C))
            scaled_B = scaled_B + [0] * (max_len - len(scaled_B))
            C = [x ^ y for x, y in zip(C, scaled_B)]
            if 2 * L <= i:
                L = i + 1 - L
                B = T
                b = d
                m = 1
            else:
                m += 1
    return C

def chien_search(err_locator, length):
    err_locs = []
    for i in range(length):
        val = 0
        for j, coef in enumerate(err_locator):
            val ^= gf_mul(coef, gf_pow(2, (j * i) % 255))
        if val == 0:
            err_locs.append(255 - i)
    return err_locs

def get_block_config(version, ecc_level):
    # ecc_level: 1=L, 0=M, 3=Q, 2=H
    # Returns [(num_blocks, data_codewords_per_block, ecc_codewords_per_block), ...]
    config = {
        1: {1: [(1, 19, 7)], 0: [(1, 16, 10)], 3: [(1, 13, 13)], 2: [(1, 9, 17)]},
        2: {1: [(1, 34, 10)], 0: [(1, 28, 16)], 3: [(1, 22, 22)], 2: [(1, 16, 28)]},
        3: {1: [(1, 55, 15)], 0: [(1, 44, 26)], 3: [(2, 17, 18)], 2: [(2, 13, 22)]},
        4: {1: [(1, 80, 20)], 0: [(2, 32, 18)], 3: [(2, 24, 26)], 2: [(4, 9, 16)]}
    }
    return config.get(version, {}).get(ecc_level, [(1, 19, 7)])

def correct_errors(bits, size, ecc_level):
    if len(bits) % 8 != 0:
        bits = bits + [0] * (8 - len(bits) % 8)
    codewords = [int(''.join(str(b) for b in bits[i:i+8]), 2) for i in range(0, len(bits), 8)]
    
    version = (size - 21) // 4 + 1
    blocks = get_block_config(version, ecc_level)
    
    total_data = sum(n * d for n, d, e in blocks)
    total_ecc = sum(n * e for n, d, e in blocks)
    total_codewords = total_data + total_ecc
    
    if len(codewords) < total_codewords:
        codewords += [0] * (total_codewords - len(codewords))
    
    # De-interleave blocks
    num_blocks = sum(n for n, d, e in blocks)
    data_blocks = [[] for _ in range(num_blocks)]
    ecc_blocks = [[] for _ in range(num_blocks)]
    
    idx = 0
    # De-interleave data
    max_data = max(d for n, d, e in blocks)
    for c in range(max_data):
        for r in range(num_blocks):
            if c < blocks[0][1]: # simplifying for equal blocks
                data_blocks[r].append(codewords[idx])
                idx += 1
                
    # De-interleave ECC
    max_ecc = max(e for n, d, e in blocks)
    for c in range(max_ecc):
        for r in range(num_blocks):
            ecc_blocks[r].append(codewords[idx])
            idx += 1
            
    out_bits = []
    for b_idx in range(num_blocks):
        data = data_blocks[b_idx]
        ecc = ecc_blocks[b_idx]
        synd = [0] * len(ecc)
        for i in range(len(ecc)):
            val = 0
            for j, cw in enumerate(data + ecc):
                if cw != 0:
                    val ^= gf_mul(cw, gf_pow(2, (i * j) % 255))
            synd[i] = val
        if any(synd):
            err_loc = berlekamp_massey(synd)
            err_positions = chien_search(err_loc, len(data) + len(ecc))
        for cw in data:
            out_bits.extend([int(b) for b in f"{cw:08b}"])
            
    return out_bits
