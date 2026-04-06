import cv2
import numpy as np

def robust_detect_and_connect():
    image_name = "QCM Answer Sheeta_page-0001.jpg"
    img = cv2.imread(image_name)
    
    if img is None:
        print(f"Error: Could not load '{image_name}'.")
        return None

    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = [gray[0, 0], gray[0, width-1], gray[height-1, 0], gray[height-1, width-1]]
    bg_color = np.mean(corners)
    
    if bg_color < 127:
        print("Detected dark background. Auto-inverting colors...")
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

    if len(best_4) == 4:
        print("Success! Found the 4 main triangles.")
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

        print(f"Paired: {pairs}")
        
        line_ys = []
        for i, j in pairs:
            y = (centers[i][1] + centers[j][1]) // 2
            line_ys.append(y)
            cv2.line(img, (0, y), (width, y), (255, 0, 0), 5)
            print(f"Line at y={y}")

        line_ys.sort()
        top_y = line_ys[0]
        bottom_y = line_ys[-1]

        print(f"\nDetecting circles between y={top_y} and y={bottom_y}...")

        # Use the original circle detection method
        gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred2 = cv2.GaussianBlur(gray2, (7, 7), 0)
        
        thresh2 = cv2.adaptiveThreshold(
            blurred2, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            15, 5
        )
        
        kernel2 = np.ones((3, 3), np.uint8)
        thresh2 = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel2)

        contours2, _ = cv2.findContours(thresh2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        
        for cnt in contours2:
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
                
                # Filter: only circles between the two lines
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

        print(f"\nDetected {len(final)} bubbles between lines")

        for b in final:
            cv2.circle(img, (b['x'], b['y']), b['r'], (0, 255, 0), 2)
            cv2.circle(img, (b['x'], b['y']), 2, (0, 0, 255), -1)

    else:
        print(f"Warning: Only found {len(best_4)} triangles.")
        return None

    output_name = "final_result.jpg"
    cv2.imwrite(output_name, img)
    print(f"\nSaved as: {output_name}")

    return {
        "triangles": best_4,
        "circles": final,
        "bounds": {"top": top_y, "bottom": bottom_y}
    }

if __name__ == "__main__":
    result = robust_detect_and_connect()
