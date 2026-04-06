"""
Complete Exam Sheet Scanner
Step 1: Extract question section
Step 2: Detect circles
Step 3: Extract answers
Step 4: Grade
"""

import cv2
import numpy as np
import os


class ExamSheetScanner:
    """Complete scanner for exam sheets."""
    
    def __init__(self):
        self.original = None
        self.questions_only = None
        self.circles = []
        self.grid = []
        self.answers = {}
        
    def load(self, image_path):
        """Load exam sheet image."""
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"Could not load: {image_path}")
        print(f"✅ Loaded: {image_path}")
        return self.original
    
    def extract_questions_section(self, top_pct=0.15, bottom_pct=0.15):
        """
        Extract only the question section.
        
        Args:
            top_pct: Percentage to cut from top (ignores header)
            bottom_pct: Percentage to cut from bottom (ignores footer)
        """
        if self.original is None:
            raise ValueError("No image loaded")
        
        h, w = self.original.shape[:2]
        
        top_cut = int(h * top_pct)
        bottom_cut = int(h * (1 - bottom_pct))
        
        self.questions_only = self.original[top_cut:bottom_cut, :]
        
        print(f"✂️  Cropped to question section:")
        print(f"   Top cut: {top_pct*100:.0f}% ({top_cut}px)")
        print(f"   Bottom cut: {bottom_pct*100:.0f}% ({h-bottom_cut}px)")
        print(f"   Size: {w}x{bottom_cut-top_cut}")
        
        return self.questions_only
    
    def extract_by_markers(self):
        """
        Automatically detect question section using black marker bars.
        Looks for solid black horizontal bars at top and bottom.
        """
        if self.original is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
        
        row_darkness = thresh.sum(axis=1) / 255
        
        threshold = w * 0.8
        
        top_marker = None
        bottom_marker = None
        
        for y in range(h // 10):
            if row_darkness[y] > threshold:
                top_marker = y
                break
        
        for y in range(h - 1, h - h // 10, -1):
            if row_darkness[y] > threshold:
                bottom_marker = y
                break
        
        if top_marker and bottom_marker:
            self.questions_only = self.original[top_marker:bottom_marker+1, :]
            print(f"✂️  Detected markers automatically:")
            print(f"   Top marker: row {top_marker}")
            print(f"   Bottom marker: row {bottom_marker}")
            print(f"   Size: {w}x{bottom_marker-top_marker+1}")
        else:
            print("⚠️  Markers not detected, using default crop")
            self.extract_questions_section(0.15, 0.15)
        
        return self.questions_only
    
    def detect_circles(self, image=None, expected_per_row=4):
        """Detect circles in the questions section."""
        if image is None:
            image = self.questions_only if self.questions_only is not None else self.original
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        h, w = gray.shape
        
        blurred = cv2.medianBlur(gray, 3)
        
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        
        avg_area = (w * h) / 10000
        
        min_area = max(50, avg_area * 0.3)
        max_area = max(400, avg_area * 2)
        
        circles = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue
            
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.5:
                continue
            
            x, y, cw, ch = cv2.boundingRect(cnt)
            aspect = cw / ch if ch > 0 else 0
            if aspect < 0.5 or aspect > 2.0:
                continue
            
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            
            too_close = False
            for px, py, _ in circles:
                if np.sqrt((cx-px)**2 + (cy-py)**2) < 20:
                    too_close = True
                    break
            
            if not too_close:
                circles.append((int(cx), int(cy), int(radius)))
        
        self.circles = sorted(circles, key=lambda c: (c[1], c[0]))
        
        print(f"\n🔍 Detected {len(self.circles)} circles")
        print(f"   Area range: {min_area:.0f} - {max_area:.0f}")
        
        return self.circles
    
    def create_grid(self, questions_per_page=20, options_per_question=4):
        """Organize circles into question grid."""
        if not self.circles:
            print("⚠️  No circles detected")
            return []
        
        h = self.questions_only.shape[0] if self.questions_only is not None else self.original.shape[0]
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
        print(f"   Questions: {len(grid)}")
        for i, row in enumerate(grid[:5]):
            print(f"   Q{i+1}: {len(row)} options")
        if len(grid) > 5:
            print(f"   ... and {len(grid)-5} more questions")
        
        return grid
    
    def detect_filled(self, image=None):
        """
        Detect which bubbles are filled.
        Uses pixel density inside each circle.
        """
        if image is None:
            image = self.questions_only if self.questions_only is not None else self.original
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        answers = {}
        options = ['A', 'B', 'C', 'D', 'E', 'F']
        
        for q_idx, row in enumerate(self.grid):
            filled_idx = -1
            max_darkness = 0
            
            for c_idx, (cx, cy, r) in enumerate(row):
                mask = np.zeros(gray.shape[:2], dtype=np.uint8)
                cv2.circle(mask, (cx, cy), max(1, r-1), 255, -1)
                
                mean_val = cv2.mean(gray, mask=mask)[0]
                darkness = 255 - mean_val
                
                if darkness > max_darkness and darkness > 30:
                    max_darkness = darkness
                    filled_idx = c_idx
            
            if filled_idx >= 0 and filled_idx < len(options):
                answer = options[filled_idx]
            else:
                answer = "?"
            
            answers[q_idx + 1] = {
                'answer': answer,
                'index': filled_idx,
                'confidence': max_darkness
            }
        
        self.answers = answers
        
        print(f"\n📝 Detected answers:")
        for q_num in sorted(answers.keys())[:10]:
            ans = answers[q_num]
            print(f"   Q{q_num}: {ans['answer']} (confidence: {ans['confidence']:.1f})")
        if len(answers) > 10:
            print(f"   ... and {len(answers)-10} more")
        
        return answers
    
    def save_visualization(self, output_path):
        """Save image with detected circles and answers labeled."""
        if self.questions_only is not None:
            img = self.questions_only.copy()
        else:
            img = self.original.copy()
        
        for q_idx, row in enumerate(self.grid):
            for c_idx, (cx, cy, r) in enumerate(row):
                answer = self.answers.get(q_idx + 1, {})
                is_filled = answer.get('index') == c_idx
                
                color = (0, 255, 0) if is_filled else (128, 128, 128)
                thickness = 3 if is_filled else 1
                
                cv2.circle(img, (cx, cy), r, color, thickness)
                cv2.circle(img, (cx, cy), 2, (0, 0, 255), -1)
                
                label = f"Q{q_idx+1}"
                cv2.putText(
                    img, label,
                    (cx - 15, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1
                )
        
        cv2.imwrite(output_path, img)
        print(f"💾 Saved visualization: {output_path}")
        
        return img
    
    def run_full_scan(self, image_path, top_crop=0.15, bottom_crop=0.15):
        """
        Run complete scanning pipeline.
        
        Args:
            image_path: Path to exam sheet image
            top_crop: % to cut from top (header)
            bottom_crop: % to cut from bottom (footer)
        
        Returns:
            Dictionary of detected answers
        """
        print("\n" + "="*60)
        print("EXAM SHEET SCANNER")
        print("="*60)
        
        self.load(image_path)
        
        print("\n🔍 Trying to detect marker bars...")
        self.extract_by_markers()
        
        self.detect_circles()
        self.create_grid()
        self.detect_filled()
        
        print("="*60)
        print("✅ SCAN COMPLETE")
        print("="*60)
        
        return self.answers


def scan_exam(image_path, output_path=None, top_crop=0.15, bottom_crop=0.15):
    """
    Scan an exam sheet and return detected answers.
    
    Args:
        image_path: Path to the scanned exam sheet
        output_path: Path to save visualization (optional)
        top_crop: % to crop from top (0.15 = 15%)
        bottom_crop: % to crop from bottom (0.15 = 15%)
    
    Returns:
        Dictionary: {question_number: {'answer': 'A', 'index': 0, 'confidence': 45.2}}
    """
    scanner = ExamSheetScanner()
    answers = scanner.run_full_scan(image_path, top_crop, bottom_crop)
    
    if output_path:
        scanner.save_visualization(output_path)
    
    return answers, scanner


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python exam_scanner.py <image_path> [output_path] [top_crop] [bottom_crop]")
        print("\nExamples:")
        print("  python exam_scanner.py sheet.jpg")
        print("  python exam_scanner.py sheet.jpg result.png 0.12 0.15")
        print("  python exam_scanner.py sheet.jpg result.png 0.15 0.20")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    top_crop = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
    bottom_crop = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
    
    answers, scanner = scan_exam(image_path, output_path, top_crop, bottom_crop)
    
    print(f"\n📊 Final Results:")
    print(f"   Total questions: {len(answers)}")
    filled = sum(1 for a in answers.values() if a['answer'] != '?')
    print(f"   Answers detected: {filled}")
    
    print("\n📝 Answers:")
    for q_num in sorted(answers.keys()):
        print(f"   Q{q_num}: {answers[q_num]['answer']}")
