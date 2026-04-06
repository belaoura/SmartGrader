"""
Image Preprocessing Module for SmartGrader
Converts scanned exam sheets into optimal format for circle detection.
"""

import cv2
import numpy as np
import os


class ImagePreprocessor:
    """Preprocesses exam sheet images for better circle detection."""
    
    def __init__(self, image_path=None):
        self.image_path = image_path
        self.original = None
        self.gray = None
        self.processed = None
        self.debug_images = {}
        
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path):
        """Load image from file."""
        self.image_path = image_path
        self.original = cv2.imread(image_path)
        
        if self.original is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        print(f"✅ Image loaded: {image_path}")
        print(f"   Size: {self.original.shape[1]}x{self.original.shape[0]}")
        return self.original
    
    def to_grayscale(self):
        """Convert image to grayscale."""
        if self.original is None:
            raise ValueError("No image loaded")
        
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.debug_images['grayscale'] = self.gray
        print("✅ Converted to grayscale")
        return self.gray
    
    def reduce_noise(self, kernel_size=5):
        """Apply Gaussian blur to reduce noise."""
        if self.gray is None:
            self.to_grayscale()
        
        self.processed = cv2.GaussianBlur(self.gray, (kernel_size, kernel_size), 0)
        self.debug_images['noise_reduced'] = self.processed
        print(f"✅ Noise reduced (kernel={kernel_size})")
        return self.processed
    
    def enhance_contrast(self):
        """Enhance contrast using CLAHE."""
        if self.gray is None:
            self.to_grayscale()
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(self.gray)
        self.processed = enhanced
        self.debug_images['contrast_enhanced'] = self.processed
        print("✅ Contrast enhanced")
        return self.processed
    
    def threshold(self, method='otsu', block_size=11, c=2):
        """
        Apply thresholding to separate bubbles from background.
        
        Methods:
        - 'otsu': Automatic threshold (good for general use)
        - 'adaptive': Adaptive threshold (good for uneven lighting)
        - 'binary': Simple binary threshold
        """
        if self.gray is None:
            self.to_grayscale()
        
        if method == 'otsu':
            _, thresh = cv2.threshold(
                self.gray, 0, 255, 
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
        elif method == 'adaptive':
            thresh = cv2.adaptiveThreshold(
                self.gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                block_size, c
            )
        elif method == 'binary':
            _, thresh = cv2.threshold(
                self.gray, 127, 255,
                cv2.THRESH_BINARY_INV
            )
        else:
            raise ValueError(f"Unknown threshold method: {method}")
        
        self.processed = thresh
        self.debug_images['threshold'] = self.processed
        print(f"✅ Threshold applied ({method})")
        return self.processed
    
    def deskew(self):
        """
        Detect and correct sheet rotation (deskew).
        Uses Hough line detection to find edges.
        """
        if self.original is None:
            raise ValueError("No image loaded")
        
        gray = self.gray if self.gray is not None else self.to_grayscale()
        
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is None:
            print("⚠️  No lines detected, image might already be straight")
            return self.original
        
        angles = []
        for line in lines[:50]:  # Check first 50 lines
            rho, theta = line[0]
            if theta > np.pi/4 and theta < 3*np.pi/4:
                angles.append(np.degrees(theta) - 90)
        
        if not angles:
            print("⚠️  Could not determine rotation angle")
            return self.original
        
        median_angle = np.median(angles)
        
        if abs(median_angle) < 0.5:
            print(f"✅ Image is straight (angle: {median_angle:.2f}°)")
            return self.original
        
        h, w = self.original.shape[:2]
        center = (w // 2, h // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        deskewed = cv2.warpAffine(
            self.original, rotation_matrix, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        self.original = deskewed
        if self.gray is not None:
            self.gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
        
        print(f"✅ Deskewed: rotated {median_angle:.2f}°")
        self.debug_images['deskewed'] = deskewed
        return deskewed
    
    def crop_margins(self, top=50, bottom=50, left=50, right=50):
        """Crop margins from the image."""
        if self.original is None:
            raise ValueError("No image loaded")
        
        h, w = self.original.shape[:2]
        cropped = self.original[
            top:h-bottom,
            left:w-right
        ]
        
        self.original = cropped
        if self.gray is not None:
            self.gray = self.gray[top:h-bottom, left:w-right]
        if self.processed is not None:
            self.processed = self.processed[top:h-bottom, left:w-right]
        
        print(f"✅ Cropped margins: top={top}, bottom={bottom}, left={left}, right={right}")
        return cropped
    
    def auto_crop(self):
        """Automatically detect and crop the exam area using edge detection."""
        if self.original is None:
            raise ValueError("No image loaded")
        
        gray = self.gray if self.gray is not None else self.to_grayscale()
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            print("⚠️  No contours found")
            return self.original
        
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        area = w * h
        img_area = self.original.shape[0] * self.original.shape[1]
        
        if area < img_area * 0.5:
            print("⚠️  Detected area too small, keeping original")
            return self.original
        
        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(self.original.shape[1] - x, w + 2*margin)
        h = min(self.original.shape[0] - y, h + 2*margin)
        
        cropped = self.original[y:y+h, x:x+w]
        
        self.original = cropped
        if self.gray is not None:
            self.gray = self.gray[y:y+h, x:x+w]
        if self.processed is not None:
            self.processed = self.processed[y:y+h, x:x+w]
        
        print(f"✅ Auto-cropped: {w}x{h} at ({x}, {y})")
        self.debug_images['auto_cropped'] = cropped
        return cropped
    
    def full_preprocess(self, deskew_flag=True, auto_crop_flag=True):
        """
        Apply full preprocessing pipeline.
        
        Pipeline:
        1. Load (already done)
        2. Deskew (optional)
        3. Crop (optional)
        4. Grayscale
        5. Noise reduction
        6. Contrast enhancement
        7. Thresholding
        """
        print("\n" + "="*50)
        print("PREPROCESSING PIPELINE")
        print("="*50)
        
        if deskew_flag:
            self.deskew()
        
        if auto_crop_flag:
            self.auto_crop()
        
        self.to_grayscale()
        self.reduce_noise(kernel_size=5)
        self.enhance_contrast()
        self.threshold(method='otsu')
        
        print("="*50)
        print("✅ PREPROCESSING COMPLETE")
        print("="*50)
        
        return self.processed
    
    def save_debug_images(self, output_dir):
        """Save all debug images for inspection."""
        os.makedirs(output_dir, exist_ok=True)
        
        save_map = {
            '01_original': self.original,
            '02_grayscale': self.gray,
            '03_noise_reduced': self.debug_images.get('noise_reduced'),
            '04_contrast_enhanced': self.debug_images.get('contrast_enhanced'),
            '05_threshold': self.processed,
        }
        
        for name, img in save_map.items():
            if img is not None:
                filepath = os.path.join(output_dir, f"{name}.png")
                cv2.imwrite(filepath, img)
                print(f"💾 Saved: {filepath}")
    
    def show_image(self, window_name="Image", image=None):
        """Display image (for debugging)."""
        if image is None:
            image = self.processed if self.processed is not None else self.original
        
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def preprocess_sheet(image_path, output_dir=None, save_debug=True):
    """
    Preprocess an exam sheet image.
    
    Args:
        image_path: Path to the input image
        output_dir: Directory to save debug images (optional)
        save_debug: Whether to save intermediate results
    
    Returns:
        Preprocessed image ready for circle detection
    """
    preprocessor = ImagePreprocessor(image_path)
    result = preprocessor.full_preprocess()
    
    if save_debug and output_dir:
        preprocessor.save_debug_images(output_dir)
    
    return result, preprocessor


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocessing.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python preprocessing.py exam_sheet.jpg")
        print("  python preprocessing.py exam_sheet.jpg debug_output/")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "debug_output"
    
    try:
        result, preprocessor = preprocess_sheet(image_path, output_dir)
        print(f"\n✅ Done! Preprocessed image ready.")
        print(f"   Output size: {result.shape[1]}x{result.shape[0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
