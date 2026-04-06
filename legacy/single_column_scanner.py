"""
Smart Circle Detection for Single-Column MCQ
Detects circles ONLY in the question zone, organized in one column.
"""

import cv2
import numpy as np
import os

# ============================================
# 📁 EDIT THIS: Your file name here
# ============================================
INPUT_FILE = "sheet_image.png"  # Use: JPG, PNG, BMP
OUTPUT_FILE = "result.png"      # Output image name
# ============================================


class SingleColumnScanner:
    """Scanner for single-column MCQ sheets with uniform circles."""
    
    def __init__(self):
        self.original = None
        self.gray = None
        self.question_zone = None
        self.circles = []
        self.answers = {}
    
    def load(self, file_path):
        """Load image file."""
        self.original = cv2.imread(file_path)
        if self.original is None:
            raise ValueError(f"Could not load: {file_path}")
        print(f"✅ Loaded: {file_path} ({self.original.shape[1]}x{self.original.shape[0]})")
        return self.original
    
    def find_section_markers(self):
        """
        Find the black section markers to identify question zone.
        Looks for black squares at left/right edges.
        """
        if self.original is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
        
        top_y = None
        bottom_y = None
        
        for y in range(h // 10):
            row = thresh[y, :]
            dark_pixels = np.sum(row > 100)
            if dark_pixels > w * 0.1:
                top_y = y
                break
        
        for y in range(h - 1, h - h // 10, -1):
            row = thresh[y, :]
            dark_pixels = np.sum(row > 100)
            if dark_pixels > w * 0.1:
                bottom_y = y
                break
        
        if top_y and bottom_y:
            self.question_zone = self.original[top_y:bottom_y+1, :]
            print(f"✂️  Question zone detected:")
            print(f"   Top marker: row {top_y}")
            print(f"   Bottom marker: row {bottom_y}")
            print(f"   Zone size: {w}x{bottom_y-top_y+1}")
        else:
            print("⚠️  Could not detect markers")
            self.question_zone = self.original
        
        return self.question_zone
    
    def detect_circles_uniform(self, expected_size=None):
        """
        Detect circles of UNIFORM size in the question zone.
        Ignores letters and other shapes.
        """
        if self.question_zone is None:
            self.find_section_markers()
        
        zone = self.question_zone
        gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)
        
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        all_circles = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if area < 30 or area > 800:
                continue
            
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.6:
                continue
            
            x, y, cw, ch = cv2.boundingRect(cnt)
            
            aspect = cw / ch if ch > 0 else 0
            if aspect < 0.6 or aspect > 1.6:
                continue
            
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            area_circle = np.pi * radius * radius
            
            if area_circle > 0:
                extent = area / area_circle
                if extent < 0.5 or extent > 1.3:
                    continue
            
            all_circles.append({
                'x': int(cx),
                'y': int(cy),
                'r': int(radius),
                'area': area
            })
        
        if not all_circles:
            print("⚠️  No circles detected")
            return []
        
        areas = [c['area'] for c in all_circles]
        median_area = np.median(areas)
        
        if expected_size:
            target_area = expected_size
        else:
            target_area = median_area
        
        tolerance = target_area * 0.5
        
        self.circles = [
            c for c in all_circles
            if abs(c['area'] - target_area) < tolerance
        ]
        
        self.circles.sort(key=lambda c: c['y'])
        
        print(f"\n🔍 Found {len(self.circles)} circles (uniform size)")
        
        return self.circles
    
    def group_into_questions(self, options_per_question=4):
        """Group circles into questions (each question has 4 circles vertically)."""
        if not self.circles:
            print("⚠️  No circles to group")
            return []
        
        zone = self.question_zone
        h = zone.shape[0]
        
        row_height = h / (len(self.circles) / options_per_question)
        
        questions = []
        current_row = []
        current_y = None
        
        for circle in self.circles:
            if current_y is None:
                current_y = circle['y']
                current_row = [circle]
            else:
                if abs(circle['y'] - current_y) < row_height * 0.6:
                    current_row.append(circle)
                else:
                    if current_row:
                        current_row.sort(key=lambda c: c['y'])
                        questions.append(current_row)
                    current_row = [circle]
                    current_y = circle['y']
        
        if current_row:
            current_row.sort(key=lambda c: c['y'])
            questions.append(current_row)
        
        valid_questions = [q for q in questions if len(q) == options_per_question]
        
        print(f"\n📊 Grouped into {len(valid_questions)} questions")
        
        for i, q in enumerate(valid_questions[:5]):
            labels = ['A', 'B', 'C', 'D']
            positions = [c['y'] for c in q]
            print(f"   Q{i+1}: {len(q)} options, y positions: {positions}")
        
        if len(valid_questions) > 5:
            print(f"   ... and {len(valid_questions)-5} more questions")
        
        return valid_questions
    
    def detect_filled(self, questions):
        """Detect which bubble is filled (darkest inside)."""
        if self.question_zone is None:
            self.question_zone = self.original
        
        zone = self.question_zone
        gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        
        results = {}
        options = ['A', 'B', 'C', 'D']
        
        for q_idx, question in enumerate(questions):
            best_idx = -1
            best_darkness = 0
            
            for c_idx, circle in enumerate(question):
                cx, cy, r = circle['x'], circle['y'], circle['r']
                
                mask = np.zeros(gray.shape[:2], dtype=np.uint8)
                cv2.circle(mask, (cx, cy), max(1, r-1), 255, -1)
                
                mean_val = cv2.mean(gray, mask=mask)[0]
                darkness = 255 - mean_val
                
                if darkness > best_darkness and darkness > 40:
                    best_darkness = darkness
                    best_idx = c_idx
            
            if best_idx >= 0:
                answer = options[best_idx]
            else:
                answer = '?'
            
            results[q_idx + 1] = {
                'answer': answer,
                'index': best_idx,
                'confidence': best_darkness
            }
        
        self.answers = results
        return results
    
    def draw_results(self, output_path, questions):
        """Draw detected circles and answers on the question zone."""
        if self.question_zone is None:
            self.question_zone = self.original
        
        zone = self.question_zone.copy()
        h, w = zone.shape[:2]
        
        zone_resized = cv2.resize(zone, (w, h))
        overlay = zone_resized.copy()
        
        options = ['A', 'B', 'C', 'D']
        
        for q_idx, question in enumerate(questions):
            answer_data = self.answers.get(q_idx + 1, {})
            filled_idx = answer_data.get('index', -1)
            
            for c_idx, circle in enumerate(question):
                cx, cy, r = circle['x'], circle['y'], circle['r']
                
                is_filled = (c_idx == filled_idx)
                
                color = (0, 255, 0) if is_filled else (150, 150, 150)
                thickness = 3 if is_filled else 2
                
                cv2.circle(zone_resized, (cx, cy), r, color, thickness)
                cv2.circle(zone_resized, (cx, cy), 2, (0, 0, 255), -1)
                
                label = f"Q{q_idx+1}{options[c_idx]}"
                cv2.putText(
                    zone_resized, label,
                    (cx - 15, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1
                )
        
        cv2.imwrite(output_path, zone_resized)
        print(f"💾 Saved visualization: {output_path}")
        
        return zone_resized
    
    def run(self, image_path, output_path=None):
        """Run complete scanning pipeline."""
        print("\n" + "="*60)
        print("SINGLE COLUMN MCQ SCANNER")
        print("="*60)
        
        self.load(image_path)
        self.find_section_markers()
        self.detect_circles_uniform()
        
        if len(self.circles) > 0:
            questions = self.group_into_questions(options_per_question=4)
            if questions:
                self.detect_filled(questions)
        
        if output_path and questions:
            self.draw_results(output_path, questions)
        
        print("="*60)
        print("✅ SCAN COMPLETE")
        print("="*60)
        
        return self.answers


def scan_single_column(image_path, output_path=None):
    """Scan a single-column MCQ exam sheet."""
    scanner = SingleColumnScanner()
    return scanner.run(image_path, output_path)


if __name__ == "__main__":
    # Get the folder where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build full paths
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    
    print("="*60)
    print("SINGLE COLUMN MCQ SCANNER")
    print("="*60)
    print(f"\n📁 Input:  {INPUT_FILE}")
    print(f"📁 Output: {OUTPUT_FILE}")
    print("\nSupported: HTML, PDF, JPG, PNG")
    print("="*60)
    
    if not os.path.exists(input_path):
        print(f"\n❌ File not found: {input_path}")
        print("\n💡 Edit INPUT_FILE at the top of this script.")
    else:
        answers = scan_single_column(input_path, output_path)
        
        print("\n📝 DETECTED ANSWERS:")
        for q_num in sorted(answers.keys()):
            ans = answers[q_num]
            print(f"   Q{q_num}: {ans['answer']} (confidence: {ans['confidence']:.1f})")
