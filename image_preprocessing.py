import sys, site

def _add_user_site():
    try:
        sp = site.getusersitepackages()
        if sp not in sys.path:
            sys.path.append(sp)
    except Exception:
        pass
    
_add_user_site()
from PIL import Image, ImageFilter
import numpy as np

def apply_morphological_closing(img_array):
    padded = np.pad(img_array, 1, mode='constant', constant_values=255)
    eroded = np.zeros_like(img_array)
    for r in range(img_array.shape[0]):
        for c in range(img_array.shape[1]):
            eroded[r, c] = np.min(padded[r:r+3, c:c+3])
    return eroded

def load_image(path):
    img = Image.open(path).convert('L')
    img = img.filter(ImageFilter.MedianFilter(size=3))
    arr = np.array(img)
    threshold = np.mean(arr) * 0.95
    thresh = np.where(arr < threshold, 0, 255).astype(np.uint8)
    return apply_morphological_closing(thresh)
