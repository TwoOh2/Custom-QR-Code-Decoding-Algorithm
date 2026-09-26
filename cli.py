import argparse
import sys
from image_preprocessing import load_image
from pattern_detection import find_finder_patterns
from perspective import correct_perspective
from grid_sampler import sample_grid
from format_info import decode_format_info
from unmasker import apply_unmask
from extractor import extract_bits
from reed_solomon import correct_errors
from decoder import decode_bits

def print_ascii_matrix(matrix):
    size = matrix.shape[0]
    print("\n--- QR Code Ascii Visualization ---")
    for r in range(size):
        row_str = ""
        for c in range(size):
            if matrix[r, c] == 1:
                row_str += "██"
            else:
                row_str += "  "
        print(row_str)
    print("-" * (size * 2))

def run_cli():
    parser = argparse.ArgumentParser(description="Custom QR Code Decoder CLI")
    parser.add_argument("image", help="Path to the QR code image")
    parser.add_argument("--visualize", action="store_true", help="Print the ASCII unmasked matrix")
    parser.add_argument("--verbose", action="store_true", help="Print step-by-step debug information")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"[*] Loading image: {args.image}")
    
    img = load_image(args.image)
    patterns = find_finder_patterns(img)
    
    if not patterns or len(patterns) != 3:
        print("[!] Error: Could not detect the 3 finder patterns.")
        sys.exit(1)
        
    if args.verbose:
        print("[*] Found finder patterns. Warping perspective...")
        
    warped, size = correct_perspective(img, patterns)
    matrix = sample_grid(warped, size)
    
    if args.verbose:
        print(f"[*] Grid sampled. Detected Size: {size}x{size}")
        
    ecc_level, mask_pattern = decode_format_info(matrix)
    
    if args.verbose:
        ecc_map = {1: 'L', 0: 'M', 3: 'Q', 2: 'H'}
        print(f"[*] Format decoded -> ECC Level: {ecc_map.get(ecc_level, 'Unknown')}, Mask Pattern: {mask_pattern}")
        
    unmasked = apply_unmask(matrix, mask_pattern)
    
    if args.visualize:
        print_ascii_matrix(unmasked)
        
    raw_bits = extract_bits(unmasked)
    
    if args.verbose:
        print(f"[*] Extracted {len(raw_bits)} bits.")
        
    corrected = correct_errors(raw_bits, size, ecc_level)
    
    if args.verbose:
        print(f"[*] Error correction applied. Remaining bits: {len(corrected)}")
        
    version = (size - 21) // 4 + 1
    result = decode_bits(corrected, version)
    
    if result is not None:
        print(f"\n[+] DECODED RESULT: {result}\n")
    else:
        print("\n[-] Error: Failed to parse character encoding stream.\n")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
