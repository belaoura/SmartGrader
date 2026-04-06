"""
Circle Detection Module for SmartGrader
Uses Hough Transform to detect answer bubbles on exam sheets.
"""

import cv2
import numpy as np
import os


class CircleDetector:
    """Detects circles (answer bubbles) on exam sheets using Hough Transform."""
    
    def __init__(self, image=None):
        self.image = image
        self.gray = None
        self.circles = []
        self.detected_circles = []
        self.question_grid = []
        
    def load_image(self, image_path):
        """Load image from file."""
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        print(f"✅ Image loaded: {image_path}")
        return self.image
    
    def set_image(self, image):
        """Set image directly (from preprocessing)."""
        self.image = image
        return image
    
    def to_grayscale(self):
        """Convert to grayscale."""
        if self.image is None:
            raise ValueError("No image loaded")
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return self.gray
    
    def detect_circles(
        self,
        min_radius=10,
        max_radius=30,
        dp=1,
        min_dist=20,
        param1=100,
        param2=30,
        blur_kernel=5
    ):
        """
        Detect circles using Hough Transform.
        
        Args:
            min_radius: Minimum circle radius (pixels)
            max_radius: Maximum circle radius (pixels)
            dp: Inverse ratio of resolution (1 = same)
            min_dist: Minimum distance between circles
            param1: Upper threshold for Canny edge detector
            param2: Threshold for center detection (lower = more circles)
            blur_kernel: Gaussian blur kernel size
        
        Returns:
            Array of detected circles
        """
        if self.image is None:
            raise ValueError("No image loaded")
        
        if self.gray is None:
            self.to_grayscale()
        
        blurred = cv2.GaussianBlur(self.gray, (blur_kernel, blur_kernel), 0)
        
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=min_dist,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        if circles is not None:
            self.circles = np.uint16(np.around(circles))
            print(f"✅ Detected {len(self.circles[0])} circles")
        else:
            self.circles = np.array([])
            print("⚠️  No circles detected")
        
        return self.circles
    
    def detect_circles_auto(self):
        """
        Auto-detect circles with optimized parameters for exam sheets.
        Uses adaptive parameters based on image size.
        """
        if self.image is None:
            raise ValueError("No image loaded")
        
        h, w = self.image.shape[:2]
        img_area = h * w
        
        avg_dimension = (h + w) / 2
        
        if avg_dimension < 1000:
            scale = "small"
            min_r, max_r = 8, 20
            min_dist = 15
        elif avg_dimension < 2000:
            scale = "medium"
            min_r, max_r = 12, 30
            min_dist = 25
        else:
            scale = "large"
            min_r, max_r = 15, 40
            min_dist = 35
        
        print(f"📐 Image {scale} ({w}x{h}), using radius {min_r}-{max_r}")
        
        return self.detect_circles(
            min_radius=min_r,
            max_radius=max_r,
            min_dist=min_dist,
            param1=150,
            param2=25,
            blur_kernel=5
        )
    
    def filter_duplicates(self, distance_threshold=10):
        """
        Remove duplicate circles that are too close.
        Keep the one with the strongest response.
        """
        if len(self.circles) == 0:
            return np.array([])
        
        circles = self.circles[0]
        filtered = []
        
        for circle in circles:
            x, y, r = circle
            is_duplicate = False
            
            for fx, fy, fr in filtered:
                dist = np.sqrt((x - fx)**2 + (y - fy)**2)
                if dist < distance_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append([x, y, r])
        
        self.detected_circles = np.array([[f] for f in filtered], dtype=np.int16)
        print(f"✅ After filtering: {len(self.detected_circles[0])} circles")
        
        return self.detected_circles
    
    def group_into_grid(self, rows_per_page=20, cols_per_row=4):
        """
        Group detected circles into a question grid.
        
        Args:
            rows_per_page: Number of questions per page
            cols_per_row: Number of options per question (usually 4 for A,B,C,D)
        
        Returns:
            Grid of circles organized by question and option
        """
        if len(self.detected_circles) == 0:
            print("⚠️  No circles to group")
            return []
        
        circles = self.detected_circles[0]
        
        if len(circles) < cols_per_row:
            print(f"⚠️  Not enough circles ({len(circles)}) for grid")
            return []
        
        sorted_by_y = sorted(circles, key=lambda c: c[1])
        
        row_height = self.image.shape[0] / rows_per_page
        
        grid = []
        current_row = []
        current_y = None
        
        for circle in sorted_by_y:
            x, y, r = circle
            
            if current_y is None:
                current_y = y
                current_row.append(circle)
            else:
                if abs(y - current_y) < row_height * 0.6:
                    current_row.append(circle)
                else:
                    if len(current_row) > 0:
                        current_row.sort(key=lambda c: c[0])
                        grid.append(current_row)
                    current_row = [circle]
                    current_y = y
        
        if len(current_row) > 0:
            current_row.sort(key=lambda c: c[0])
            grid.append(current_row)
        
        self.question_grid = grid
        
        expected = rows_per_page * cols_per_row
        detected = len(circles)
        print(f"📊 Grid created: {len(grid)} rows x {cols_per_row} cols")
        print(f"   Expected: {expected} circles, Detected: {detected}")
        
        return grid
    
    def draw_circles(self, image=None, color=(0, 255, 0), thickness=2):
        """Draw detected circles on image."""
        if image is None:
            image = self.image.copy()
        
        if len(self.circles) == 0:
            return image
        
        for circle in self.circles[0]:
            cx, cy, r = circle
            cv2.circle(image, (cx, cy), r, color, thickness)
            cv2.circle(image, (cx, cy), 2, (0, 0, 255), -1)
        
        return image
    
    def draw_grid(self, image=None, color=(0, 255, 0)):
        """Draw the question grid with labels."""
        if image is None:
            image = self.image.copy()
        
        if len(self.question_grid) == 0:
            return self.draw_circles(image, color)
        
        for row_idx, row in enumerate(self.question_grid):
            for col_idx, circle in enumerate(row):
                cx, cy, r = circle
                
                options = ['A', 'B', 'C', 'D', 'E', 'F']
                label = options[col_idx] if col_idx < len(options) else str(col_idx)
                
                cv2.circle(image, (cx, cy), r, color, 2)
                cv2.circle(image, (cx, cy), 2, (0, 0, 255), -1)
                
                cv2.putText(
                    image, f"Q{row_idx+1}{label}",
                    (cx - 15, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1
                )
        
        return image
    
    def save_result(self, output_path, show_grid=True):
        """Save result image with detected circles."""
        if show_grid:
            result = self.draw_grid()
        else:
            result = self.draw_circles()
        
        cv2.imwrite(output_path, result)
        print(f"💾 Saved result: {output_path}")
        return result
    
    def get_circle_positions(self):
        """Get all circle positions as a list."""
        if len(self.circles) == 0:
            return []
        return [(int(x), int(y), int(r)) for x, y, r in self.circles[0]]


def detect_sheet_circles(image_path, output_path=None):
    """
    Complete circle detection pipeline.
    
    Args:
        image_path: Path to preprocessed image
        output_path: Path to save result image
    
    Returns:
        CircleDetector instance with detected circles
    """
    print("\n" + "="*50)
    print("CIRCLE DETECTION (Hough Transform)")
    print("="*50)
    
    detector = CircleDetector()
    detector.load_image(image_path)
    
    print("\n📍 Detecting circles...")
    detector.detect_circles_auto()
    
    if len(detector.circles) > 0:
        detector.filter_duplicates()
        detector.group_into_grid(rows_per_page=20, cols_per_row=4)
    
    if output_path:
        detector.save_result(output_path, show_grid=True)
    
    print("="*50)
    
    return detector


if __name__ == "__main__":
    import sys
    from preprocessing import ImagePreprocessor
    
    if len(sys.argv) < 2:
        print("Usage: python circle_detection.py <image_path> [output_path]")
        print("\nExample:")
        print("  python circle_detection.py preprocessed_sheet.png")
        print("  python circle_detection.py preprocessed_sheet.png result.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "circles_detected.png"
    
    try:
        detector = detect_sheet_circles(image_path, output_path)
        
        print(f"\n✅ Detection complete!")
        print(f"   Circles found: {len(detector.circles[0]) if len(detector.circles) > 0 else 0}")
        print(f"   Question rows: {len(detector.question_grid)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
