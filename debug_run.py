from image_preprocessing import load_image
from pattern_detection import find_finder_patterns
from perspective import correct_perspective
from grid_sampler import sample_grid
from unmasker import apply_unmask
from extractor import extract_bits
from reed_solomon import correct_errors
from decoder import decode_bits

def debug_pipeline():
    img_path = 'test_images/v1m0.png'
    print(f"Loading {img_path}...")
    img = load_image(img_path)
    print("Image loaded, shape:", img.shape)
    
    patterns = find_finder_patterns(img)
    if not patterns:
        print("FAILED: find_finder_patterns returned None (could not find the 3 squares).")
        return
    print(f"Found {len(patterns)} patterns.")
    
    warped = correct_perspective(img, patterns)
    print("Perspective corrected, shape:", warped.shape)
    
    matrix = sample_grid(warped)
    print("Grid sampled, 1s count:", matrix.sum())
    
    unmasked = apply_unmask(matrix)
    
    raw_bits = extract_bits(unmasked)
    print("Bits extracted, length:", len(raw_bits))
    print("First 20 bits:", raw_bits[:20])
    
    corrected = correct_errors(raw_bits)
    print("Bits after RS correction, length:", len(corrected))
    
    result = decode_bits(corrected)
    print("Final Decoded Result:", result)

if __name__ == "__main__":
    debug_pipeline()
