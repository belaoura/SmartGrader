"""
Sheet Section Detection
Automatically detects and crops to the question area only.
Ignores header and footer sections.
"""

import cv2
import numpy as np


class SectionDetector:
    """Detects and extracts the question section from exam sheets."""
    
    def __init__(self):
        self.image = None
        self.gray = None
        self.sections = {}
        self.question_region = None
    
    def load_image(self, image_path):
        """Load image from file."""
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        print(f"✅ Loaded: {image_path} ({self.image.shape[1]}x{self.image.shape[0]})")
        return self.image
    
    def analyze_by_horizontal_projection(self):
        """
        Uses horizontal projection to find sections.
        Looks for gaps where there are no text/shapes.
        """
        if self.image is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        h, w = thresh.shape
        
        row_sum = thresh.sum(axis=1)
        row_sum = row_sum / row_sum.max()
        
        threshold = 0.05
        
        is_content = row_sum > threshold
        
        sections = []
        current_start = None
        
        for i, has_content in enumerate(is_content):
            if has_content and current_start is None:
                current_start = i
            elif not has_content and current_start is not None:
                sections.append((current_start, i))
                current_start = None
        
        if current_start is not None:
            sections.append((current_start, h))
        
        self.sections = {'raw': sections}
        
        print(f"\n📐 Detected {len(sections)} content regions:")
        for i, (start, end) in enumerate(sections):
            height = end - start
            pct = height / h * 100
            print(f"   Section {i+1}: rows {start}-{end} ({height}px, {pct:.1f}%)")
        
        return sections
    
    def detect_question_section(self, min_questions=10):
        """
        Automatically detect the section containing MCQ questions.
        
        Heuristics:
        - Largest content section
        - Has enough vertical space (multiple questions)
        - Located in middle portion of page
        """
        if not self.sections.get('raw'):
            self.analyze_by_horizontal_projection()
        
        sections = self.sections['raw']
        if not sections:
            print("⚠️  No sections detected")
            return None
        
        h, w = self.image.shape[:2]
        
        section_info = []
        for start, end in sections:
            height = end - start
            mid_point = (start + end) // 2
            
            section_info.append({
                'start': start,
                'end': end,
                'height': height,
                'mid': mid_point,
                'score': 0
            })
        
        for sec in section_info:
            sec['score'] = sec['height']
            
            mid_pct = sec['mid'] / h
            if 0.2 < mid_pct < 0.8:
                sec['score'] += 100
            
            if sec['height'] > h * 0.3:
                sec['score'] += 200
        
        best = max(section_info, key=lambda s: s['score'])
        
        self.question_region = (best['start'], best['end'])
        
        print(f"\n🎯 Question section: rows {best['start']}-{best['end']}")
        print(f"   Height: {best['height']}px ({best['height']/h*100:.1f}% of page)")
        
        self.sections['question'] = self.question_region
        
        return self.question_region
    
    def detect_three_sections(self):
        """
        Detect header, question body, and footer sections.
        Uses edge detection to find horizontal lines/boundaries.
        """
        if self.image is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        horizontal = np.zeros_like(edges)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180,
            threshold=100,
            minLineLength=w*0.3,
            maxLineGap=20
        )
        
        if lines is not None:
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:
                    horizontal_lines.append((min(y1, y2), max(y1, y2)))
            
            horizontal_lines.sort()
            
            boundaries = [0]
            for start, end in horizontal_lines:
                if start - boundaries[-1] > h * 0.05:
                    boundaries.append((start + end) // 2)
            boundaries.append(h)
            
            while len(boundaries) > 4:
                gaps = []
                for i in range(len(boundaries) - 1):
                    gap = boundaries[i+1] - boundaries[i]
                    gaps.append((gap, i))
                gaps.sort(reverse=True)
                del boundaries[gaps[0][1] + 1]
            
            if len(boundaries) >= 3:
                header_end = boundaries[1]
                footer_start = boundaries[2]
                
                self.sections['header'] = (0, header_end)
                self.sections['body'] = (header_end, footer_start)
                self.sections['footer'] = (footer_start, h)
        
        if not self.sections.get('body'):
            self.detect_question_section()
            self.sections['body'] = self.question_region
        
        print("\n📄 Sheet sections detected:")
        for name, region in self.sections.items():
            if region:
                start, end = region
                height = end - start
                pct = height / h * 100
                print(f"   {name}: {start}-{end}px ({pct:.1f}%)")
        
        return self.sections
    
    def crop_section(self, section_name):
        """Crop image to a specific section."""
        if not self.sections.get(section_name):
            self.detect_three_sections()
        
        region = self.sections.get(section_name)
        if not region:
            raise ValueError(f"Section '{section_name}' not found")
        
        start, end = region
        cropped = self.image[start:end, :]
        
        print(f"✂️  Cropped '{section_name}': {cropped.shape[1]}x{cropped.shape[0]}")
        
        return cropped
    
    def get_question_only(self, manual_crop=None):
        """
        Get only the question area.
        
        Args:
            manual_crop: Optional (top, bottom) tuple for manual adjustment
                        Values are percentages (0-1) of image height
        
        Returns:
            Cropped image containing only questions
        """
        if manual_crop:
            top_pct, bottom_pct = manual_crop
            h = self.image.shape[0]
            top = int(h * top_pct)
            bottom = int(h * (1 - bottom_pct))
            
            cropped = self.image[top:bottom, :]
            print(f"✂️  Manual crop: rows {top}-{bottom} ({bottom-top}px)")
            return cropped
        
        if not self.sections.get('body'):
            self.detect_three_sections()
        
        body = self.sections.get('body')
        if body:
            start, end = body
            return self.image[start:end, :]
        
        self.detect_question_section()
        if self.question_region:
            start, end = self.question_region
            return self.image[start:end, :]
        
        h, w = self.image.shape[:2]
        margin = int(h * 0.12)
        return self.image[margin:h-margin, :]
    
    def save_sections(self, output_dir):
        """Save each section as a separate image."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.sections:
            self.detect_three_sections()
        
        for name, region in self.sections.items():
            if region:
                start, end = region
                section_img = self.image[start:end, :]
                path = os.path.join(output_dir, f"section_{name}.png")
                cv2.imwrite(path, section_img)
                print(f"💾 Saved: {path}")
        
        full_crop = self.get_question_only()
        path = os.path.join(output_dir, "questions_only.png")
        cv2.imwrite(path, full_crop)
        print(f"💾 Saved: {path}")


def extract_questions(image_path, output_dir=None):
    """
    Extract question section from exam sheet.
    
    Returns:
        Cropped image containing only MCQ questions
    """
    detector = SectionDetector()
    detector.load_image(image_path)
    
    questions_img = detector.get_question_only()
    
    if output_dir:
        detector.save_sections(output_dir)
    
    return questions_img, detector


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python section_detector.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python section_detector.py sheet.jpg")
        print("  python section_detector.py sheet.jpg sections/")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    questions_img, detector = extract_questions(image_path, output_dir)
    
    print(f"\n✅ Extracted question section: {questions_img.shape[1]}x{questions_img.shape[0]}")
    
    if output_dir:
        print(f"   Sections saved to: {output_dir}")
