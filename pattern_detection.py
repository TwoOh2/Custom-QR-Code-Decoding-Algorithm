import cv2
import numpy as np

def find_finder_patterns(img):
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    squares = []
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            area = cv2.contourArea(approx)
            if area > 1000:
                squares.append((area, approx.reshape(4, 2)))
    if len(squares) < 3:
        return None
    squares.sort(key=lambda x: x[0], reverse=True)
    pts = [s[1] for s in squares[:3]]

    ordered = []
    for p in pts:
        s = p.sum(axis=1)
        diff = np.diff(p, axis=1).ravel()
        ordered.append((p[np.argmin(s)], p[np.argmax(s)], p[np.argmin(diff)], p[np.argmax(diff)]))

    return pts
