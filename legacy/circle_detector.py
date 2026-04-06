"""
Two-Column Bubble Detector with Triangle Section Detection
Detects triangles, draws lines, then detects bubbles only between the lines.
"""

import cv2
import numpy as np
import os

INPUT_FILE = "QCM Answer Sheetb_page-0001.jpg"
OUTPUT_FILE = "final_result.jpg"


def detect_triangles_and_lines(img):
    """Detect 4 triangles, link closest pairs, return line y-positions."""
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = [gray[0, 0], gray[0, width-1], gray[height-1, 0], gray[height-1, width-1]]
    bg_color = np.mean(corners)
    
    if bg_color < 127:
        gray = cv2.bitwise_not(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    found_triangles = []

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)

        if len(approx) == 3:
            area = cv2.contourArea(cnt)
            if area > 400:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    found_triangles.append({"center": (cX, cY), "area": area, "contour": approx})

    found_triangles.sort(key=lambda t: t["area"], reverse=True)
    best_4 = found_triangles[:4]

    if len(best_4) != 4:
        return None, None, None

    centers = [t["center"] for t in best_4]
    
    for t in best_4:
        cv2.drawContours(img, [t["contour"]], 0, (0, 255, 0), 3)

    linked = set()
    pairs = []
    
    for i, t1 in enumerate(centers):
        if i in linked:
            continue
        best_dist = float('inf')
        best_j = None
        for j, t2 in enumerate(centers):
            if j <= i or j in linked:
                continue
            dist = np.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)
            if dist < best_dist:
                best_dist = dist
                best_j = j
        if best_j is not None:
            pairs.append((i, best_j))
            linked.add(i)
            linked.add(best_j)

    line_ys = []
    for i, j in pairs:
        y = (centers[i][1] + centers[j][1]) // 2
        line_ys.append(y)
        cv2.line(img, (0, y), (width, y), (255, 0, 0), 5)

    line_ys.sort()
    return line_ys[0], line_ys[-1], best_4


def detect_bubbles(image_path, output_path=None):
    """Detect answer bubbles in two columns, filtered between two lines."""
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not load: {image_path}")
        return [], [], img, None
    
    print(f"Loaded: {image_path} ({img.shape[1]}x{img.shape[0]})")
    
    h, w = img.shape[:2]
    
    top_y, bottom_y, triangles = detect_triangles_and_lines(img)
    
    if top_y is None:
        print("Warning: Could not detect 4 triangles. Detecting bubbles on full image.")
        top_y, bottom_y = 0, h
    
    print(f"Detecting bubbles between y={top_y} and y={bottom_y}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15, 5
    )
    
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        if area < 80 or area > 500:
            continue
        
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < 0.75:
            continue
        
        x, y, cw, ch = cv2.boundingRect(cnt)
        aspect = cw / ch if ch > 0 else 0
        if aspect < 0.7 or aspect > 1.4:
            continue
        
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            r = int(np.sqrt(area / np.pi))
            
            if r < 8 or r > 20:
                continue
            
            if top_y < cy < bottom_y:
                bubbles.append({'x': cx, 'y': cy, 'r': r, 'area': area})
    
    final = []
    for b in bubbles:
        is_dup = False
        for f in final:
            dist = np.sqrt((b['x'] - f['x'])**2 + (b['y'] - f['y'])**2)
            if dist < 12:
                is_dup = True
                break
        if not is_dup:
            final.append(b)
    
    print(f"Detected {len(final)} bubbles")
    
    left_col = []
    right_col = []
    mid_x = w // 2
    
    for b in final:
        if b['x'] < mid_x:
            left_col.append(b)
        else:
            right_col.append(b)
    
    left_col.sort(key=lambda c: c['y'])
    right_col.sort(key=lambda c: c['y'])
    
    print(f"Left column: {len(left_col)} bubbles")
    print(f"Right column: {len(right_col)} bubbles")
    
    OPTIONS_PER_QUESTION = 4
    left_q = len(left_col) // OPTIONS_PER_QUESTION
    right_q = len(right_col) // OPTIONS_PER_QUESTION
    total_q = left_q + right_q
    
    print(f"Questions: {left_q} (left) + {right_q} (right) = {total_q} total")
    
    if output_path:
        for b in left_col + right_col:
            cv2.circle(img, (b['x'], b['y']), b['r'], (0, 255, 0), 2)
            cv2.circle(img, (b['x'], b['y']), 2, (0, 0, 255), -1)
        
        cv2.imwrite(output_path, img)
        print(f"Saved: {output_path}")
    
    return left_col, right_col, img, {"top": top_y, "bottom": bottom_y, "triangles": triangles}


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    
    print("="*50)
    print("BUBBLE DETECTOR WITH TRIANGLE SECTION DETECTION")
    print("="*50)
    
    if not os.path.exists(input_path):
        print(f"File not found: {INPUT_FILE}")
    else:
        left, right, img, bounds = detect_bubbles(input_path, output_path)
    
    print("="*50)
