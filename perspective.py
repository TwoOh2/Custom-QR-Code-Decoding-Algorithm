import cv2
import numpy as np

def correct_perspective(img, patterns):
    centers = [np.mean(p, axis=0) for p in patterns]
    sums = [c[0] + c[1] for c in centers]
    tl_idx = int(np.argmin(sums))
    bl_idx = int(np.argmax([c[1] - c[0] for c in centers]))
    tr_idx = int(np.argmax([c[0] - c[1] for c in centers]))
    tl = centers[tl_idx]
    tr = centers[tr_idx]
    bl = centers[bl_idx]
    br = tr + bl - tl
    
    fp_area = cv2.contourArea(patterns[tl_idx])
    mod_size_est = np.sqrt(fp_area / 49.0) if fp_area > 0 else 10
    dist = np.linalg.norm(tl - tr)
    mods_between = dist / mod_size_est if mod_size_est > 0 else 14
    
    version = int(round((mods_between - 14) / 4)) + 1
    version = max(1, min(4, version))
    size = 21 + 4 * (version - 1)
    
    src = np.float32([tl, tr, bl, br])
    dst = np.float32([[35, 35], [(size - 3.5)*10, 35], [35, (size - 3.5)*10], [(size - 3.5)*10, (size - 3.5)*10]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (size*10, size*10))
    return warped, size

