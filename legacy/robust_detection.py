"""
Robust Circle Detection using Contour Analysis
More reliable than Hough Transform for small exam bubbles.
"""

import cv2
import numpy as np
import os


class RobustCircleDetector:
    """Detects circles using contour analysis - more robust than Hough."""
    
    def __init__(self):
        self.image = None
        self.gray = None
        self.thresh = None
        self.circles = []
        self.grid = []
        
    def load_image(self, image_path):
        """Load image from file."""
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        print(f"✅ Loaded: {image_path} ({self.image.shape[1]}x{self.image.shape[0]})")
        return self.image
    
    def preprocess(self):
        """Preprocess image for circle detection."""
        if self.image is None:
            raise ValueError("No image loaded")
        
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.GaussianBlur(self.gray, (3, 3), 0)
        
        thresh_value, self.thresh = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        kernel = np.ones((3, 3), np.uint8)
        self.thresh = cv2.morphologyEx(self.thresh, cv2.MORPH_CLOSE, kernel)
        
        print(f"✅ Preprocessed (threshold: {thresh_value})")
        return self.thresh
    
    def detect_circles_by_contours(
        self,
        min_area=50,
        max_area=2000,
        min_circularity=0.5,
        aspect_ratio_min=0.7,
        aspect_ratio_max=1.4
    ):
        """
        Detect circles using contour analysis.
        
        Args:
            min_area: Minimum contour area
            max_area: Maximum contour area
            min_circularity: How circular (0-1), lower = more shapes
            aspect_ratio_min/max: Width/height ratio bounds
        
        Returns:
            List of (x, y, radius) tuples
        """
        if self.thresh is None:
            self.preprocess()
        
        contours, _ = cv2.findContours(
            self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        print(f"🔍 Found {len(contours)} contours")
        
        circles = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < min_area or area > max_area:
                continue
            
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < min_circularity:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if aspect_ratio < aspect_ratio_min or aspect_ratio > aspect_ratio_max:
                continue
            
            radius = int((w + h) / 4)
            cx, cy = x + w // 2, y + h // 2
            
            circles.append((cx, cy, radius))
        
        self.circles = sorted(circles, key=lambda c: (c[1], c[0]))
        
        print(f"✅ Detected {len(self.circles)} circles")
        
        return self.circles
    
    def detect_by_template_matching(self, template_size=15):
        """
        Alternative: Detect filled circles using template matching.
        Looks for dark spots (filled bubbles).
        """
        if self.gray is None:
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.bilateralFilter(self.gray, 9, 75, 75)
        
        thresh_value, thresh = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        circles = []
        img_h, img_w = self.gray.shape
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < 30 or area > 800:
                continue
            
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            is_duplicate = False
            for px, py, _ in circles:
                if abs(cx - px) < template_size and abs(cy - py) < template_size:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                radius = int(np.sqrt(area / np.pi))
                circles.append((cx, cy, radius))
        
        self.circles = sorted(circles, key=lambda c: (c[1], c[0]))
        
        print(f"✅ Template matching found {len(self.circles)} circles")
        
        return self.circles
    
    def detect_bubbles_simple(self, expected_count=80):
        """
        Simple and fast bubble detection.
        Best for uniform exam sheets.
        """
        if self.image is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.medianBlur(gray, 5)
        
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        
        circles = []
        img_h, img_w = gray.shape
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if area < 20 or area > 600:
                continue
            
            if len(cnt) < 5:
                continue
            
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            area_circle = np.pi * radius * radius
            
            if area_circle == 0:
                continue
            
            extent = area / area_circle
            
            if extent < 0.3 or extent > 1.5:
                continue
            
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                too_close = False
                for px, py, _ in circles:
                    if np.sqrt((cx-px)**2 + (cy-py)**2) < 15:
                        too_close = True
                        break
                
                if not too_close:
                    circles.append((int(cx), int(cy), int(radius)))
        
        self.circles = sorted(circles, key=lambda c: (c[1], c[0]))
        
        print(f"✅ Simple detection found {len(self.circles)} circles")
        print(f"   Expected: {expected_count}, Found: {len(self.circles)}")
        
        return self.circles
    
    def create_grid(self, questions_per_page=20, options_per_question=4):
        """
        Organize detected circles into a question grid.
        """
        if len(self.circles) == 0:
            print("⚠️  No circles to grid")
            return []
        
        h, w = self.image.shape[:2]
        row_height = h / questions_per_page
        
        grid = []
        current_row = []
        current_y = None
        
        for cx, cy, r in sorted(self.circles, key=lambda c: (c[1], c[0])):
            if current_y is None:
                current_y = cy
                current_row = [(cx, cy, r)]
            else:
                if abs(cy - current_y) < row_height * 0.7:
                    current_row.append((cx, cy, r))
                else:
                    if current_row:
                        current_row.sort(key=lambda c: c[0])
                        grid.append(current_row)
                    current_row = [(cx, cy, r)]
                    current_y = cy
        
        if current_row:
            current_row.sort(key=lambda c: c[0])
            grid.append(current_row)
        
        self.grid = grid
        
        print(f"\n📊 Grid created:")
        print(f"   Rows: {len(grid)}")
        for i, row in enumerate(grid):
            print(f"   Row {i+1}: {len(row)} circles")
        
        return grid
    
    def draw_detections(self, image=None, show_labels=True):
        """Draw detected circles on image."""
        if image is None:
            image = self.image.copy()
        
        for i, (cx, cy, r) in enumerate(self.circles):
            cv2.circle(image, (cx, cy), r, (0, 255, 0), 2)
            cv2.circle(image, (cx, cy), 2, (0, 0, 255), -1)
            
            if show_labels:
                cv2.putText(
                    image, str(i+1),
                    (cx - 5, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1
                )
        
        return image
    
    def draw_grid(self, image=None):
        """Draw grid with question numbers."""
        if image is None:
            image = self.image.copy()
        
        options = ['A', 'B', 'C', 'D', 'E', 'F']
        
        for row_idx, row in enumerate(self.grid):
            for col_idx, (cx, cy, r) in enumerate(row):
                if col_idx < len(options):
                    label = f"Q{row_idx+1}{options[col_idx]}"
                else:
                    label = f"Q{row_idx+1}_{col_idx+1}"
                
                cv2.circle(image, (cx, cy), r, (0, 255, 0), 2)
                cv2.circle(image, (cx, cy), 2, (0, 0, 255), -1)
                cv2.putText(
                    image, label,
                    (cx - 15, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1
                )
        
        return image
    
    def save_result(self, filepath, show_grid=True):
        """Save result image."""
        if show_grid and self.grid:
            result = self.draw_grid()
        else:
            result = self.draw_detections()
        
        cv2.imwrite(filepath, result)
        print(f"💾 Saved: {filepath}")
        return result


def detect_exam_sheet(image_path, output_path=None):
    """
    Complete detection pipeline.
    Tries multiple methods to find the best detection.
    """
    print("\n" + "="*60)
    print("ROBUST CIRCLE DETECTION")
    print("="*60)
    
    detector = RobustCircleDetector()
    detector.load_image(image_path)
    
    print("\n🔍 Method 1: Simple detection...")
    detector.detect_bubbles_simple()
    
    if len(detector.circles) < 10:
        print("\n🔍 Method 2: Contour analysis...")
        detector.preprocess()
        detector.detect_circles_by_contours()
    
    if len(detector.circles) > 0:
        print("\n📐 Creating grid...")
        detector.create_grid(questions_per_page=20, options_per_question=4)
    
    if output_path:
        detector.save_result(output_path, show_grid=True)
    
    print("="*60)
    
    return detector


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python robust_detection.py <image_path> [output_path]")
        print("\nExample:")
        print("  python robust_detection.py sheet.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "detected.png"
    
    detector = detect_exam_sheet(image_path, output_path)
    
    print(f"\n✅ Result: {len(detector.circles)} circles in {len(detector.grid)} rows")
