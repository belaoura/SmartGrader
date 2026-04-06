"""Triangle marker detection for exam sheet alignment."""

import logging
import cv2
import numpy as np

logger = logging.getLogger("smartgrader.scanner.marker_finder")


def find_triangles(image, min_area=400, approx_tolerance=0.05):
    """Detect triangle markers in the image.

    Returns:
        List of dicts with keys: center (x, y), area, contour.
    """
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    corners = [gray[0, 0], gray[0, width - 1], gray[height - 1, 0], gray[height - 1, width - 1]]
    if np.mean(corners) < 127:
        gray = cv2.bitwise_not(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    triangles = []

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, approx_tolerance * perimeter, True)
        if len(approx) != 3:
            continue
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        triangles.append({"center": (cx, cy), "area": area, "contour": approx})

    triangles.sort(key=lambda t: t["area"], reverse=True)
    logger.info("Found %d triangles (min_area=%d)", len(triangles), min_area)
    return triangles


def find_section_boundaries(image, triangles):
    """Find top and bottom Y boundaries from 4 triangle markers.

    Returns:
        Tuple (top_y, bottom_y) or None if fewer than 4 triangles found.
    """
    best_4 = triangles[:4]
    if len(best_4) < 4:
        logger.warning("Need 4 triangles, found %d", len(best_4))
        return None

    centers = [t["center"] for t in best_4]

    linked = set()
    pairs = []
    for i in range(len(centers)):
        if i in linked:
            continue
        best_dist = float("inf")
        best_j = None
        for j in range(len(centers)):
            if j <= i or j in linked:
                continue
            dist = np.sqrt((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2)
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

    line_ys.sort()
    top_y, bottom_y = line_ys[0], line_ys[-1]
    logger.info("Section boundaries: y=%d to y=%d", top_y, bottom_y)
    return top_y, bottom_y
