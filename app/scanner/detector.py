"""Unified bubble detector with configurable parameters."""

import logging
import cv2
import numpy as np

logger = logging.getLogger("smartgrader.scanner.detector")


class BubbleDetector:
    """Detects bubbles (filled circles) in exam sheet images."""

    def __init__(
        self,
        area_min=60,
        area_max=600,
        circularity_min=0.65,
        aspect_min=0.6,
        aspect_max=1.5,
        radius_min=6,
        radius_max=25,
        duplicate_distance=10,
    ):
        self.area_min = area_min
        self.area_max = area_max
        self.circularity_min = circularity_min
        self.aspect_min = aspect_min
        self.aspect_max = aspect_max
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.duplicate_distance = duplicate_distance

    def detect(self, image, top_y, bottom_y, margin=40):
        """Detect bubbles in the region between top_y and bottom_y."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4
        )
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        img_width = image.shape[1]
        bubbles = self._filter_contours(contours, top_y, bottom_y, img_width, margin)
        bubbles = self._remove_duplicates(bubbles)
        bubbles = self._remove_outliers(bubbles)

        logger.info("Detected %d bubbles in region y=%d..%d", len(bubbles), top_y, bottom_y)
        return bubbles

    def _filter_contours(self, contours, top_y, bottom_y, img_width, margin):
        """Filter contours to only valid bubbles."""
        left_min = int(img_width * 0.08)
        left_max = int(img_width * 0.25)
        right_min = int(img_width * 0.45)
        right_max = int(img_width * 0.75)

        bubbles = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.area_min or area > self.area_max:
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < self.circularity_min:
                continue

            x, y, cw, ch = cv2.boundingRect(cnt)
            aspect = cw / ch if ch > 0 else 0
            if aspect < self.aspect_min or aspect > self.aspect_max:
                continue

            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            r = int(np.sqrt(area / np.pi))

            if r < self.radius_min or r > self.radius_max:
                continue
            if not (top_y + margin < cy < bottom_y - margin):
                continue

            col = None
            if left_min <= cx <= left_max:
                col = "L"
            elif right_min <= cx <= right_max:
                col = "R"

            if col:
                bubbles.append({"x": cx, "y": cy, "r": r, "area": area, "col": col})

        return bubbles

    def _remove_duplicates(self, bubbles):
        """Remove duplicate detections within duplicate_distance pixels."""
        final = []
        for b in bubbles:
            is_dup = False
            for f in final:
                dist = np.sqrt((b["x"] - f["x"]) ** 2 + (b["y"] - f["y"]) ** 2)
                if dist < self.duplicate_distance:
                    is_dup = True
                    break
            if not is_dup:
                final.append(b)
        return final

    def _remove_outliers(self, bubbles, max_deviation=50):
        """Remove bubbles that deviate too far from column average X."""
        if len(bubbles) < 4:
            return bubbles

        left = [b for b in bubbles if b["col"] == "L"]
        right = [b for b in bubbles if b["col"] == "R"]

        avg_left_x = sum(b["x"] for b in left) / len(left) if left else 0
        avg_right_x = sum(b["x"] for b in right) / len(right) if right else 0

        verified = []
        for b in bubbles:
            avg_x = avg_left_x if b["col"] == "L" else avg_right_x
            if abs(b["x"] - avg_x) <= max_deviation:
                verified.append(b)

        removed = len(bubbles) - len(verified)
        if removed > 0:
            logger.debug("Removed %d outlier bubbles", removed)
        return verified


def check_if_filled(image, bubble, fill_threshold=50):
    """Check if a bubble is filled by counting dark pixels."""
    x, y, r = bubble["x"], bubble["y"], bubble["r"]
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dark_pixels = cv2.countNonZero(cv2.bitwise_not(gray) & mask)
    total_pixels = cv2.countNonZero(mask)

    if total_pixels == 0:
        return False, 0.0

    fill_pct = (dark_pixels / total_pixels) * 100
    return fill_pct >= fill_threshold, fill_pct
