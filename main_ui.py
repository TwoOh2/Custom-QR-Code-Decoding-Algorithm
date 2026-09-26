import tkinter as tk
from tkinter import filedialog, messagebox
from image_preprocessing import load_image
from pattern_detection import find_finder_patterns
from perspective import correct_perspective
from grid_sampler import sample_grid
from unmasker import apply_unmask
from extractor import extract_bits
from reed_solomon import correct_errors
from decoder import decode_bits

from format_info import decode_format_info

def decode_qr(image_path):
    img = load_image(image_path)
    patterns = find_finder_patterns(img)
    if patterns is None or len(patterns) != 3:
        return None
    warped, size = correct_perspective(img, patterns)
    matrix = sample_grid(warped, size)
    
    # Advanced: Parse Format Info with BCH Decoder
    ecc_level, mask_pattern = decode_format_info(matrix)
    
    # Apply correct mask
    unmasked = apply_unmask(matrix, mask_pattern)
    
    # Extract data bits
    raw_bits = extract_bits(unmasked)
    
    # Advanced: Block de-interleaving and Error Correction
    corrected = correct_errors(raw_bits, size, ecc_level)
    
    # Advanced: Multi-mode parsing
    version = (size - 21) // 4 + 1
    return decode_bits(corrected, version)


def select_file():
    path = filedialog.askopenfilename(filetypes=[('Image Files', ('*.png', '*.jpg', '*.jpeg', '*.bmp'))])
    if not path:
        return
    result = decode_qr(path)
    if result is None:
        messagebox.showerror('Error', 'Failed to decode QR code')
    else:
        output.delete('1.0', tk.END)
        output.insert(tk.END, result)

root = tk.Tk()
root.title('QR Decoder')
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()
btn = tk.Button(frame, text='Select QR Image', command=select_file)
btn.pack(pady=5)
output = tk.Text(frame, height=4, width=50)
output.pack(pady=5)
root.mainloop()
