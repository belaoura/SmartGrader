"""Image preprocessing pipeline for scanned exam sheets."""

import logging
import cv2
import numpy as np
import os

logger = logging.getLogger("smartgrader.scanner.preprocessor")


class ImagePreprocessor:
    """Preprocesses exam sheet images for bubble detection."""

    def __init__(self):
        self.original = None
        self.gray = None
        self.processed = None
        self.debug_images = {}

    def load_image(self, image_path):
        """Load image from file path."""
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"Could not load image: {image_path}")
        logger.info("Loaded image: %s (%dx%d)", image_path, self.original.shape[1], self.original.shape[0])
        return self.original

    def load_from_array(self, image_array):
        """Load image from numpy array."""
        self.original = image_array.copy()
        logger.info("Loaded image from array (%dx%d)", self.original.shape[1], self.original.shape[0])
        return self.original

    def to_grayscale(self):
        """Convert image to grayscale."""
        if self.original is None:
            raise ValueError("No image loaded")
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.debug_images["grayscale"] = self.gray
        logger.debug("Converted to grayscale")
        return self.gray

    def reduce_noise(self, kernel_size=5):
        """Apply Gaussian blur to reduce noise."""
        if self.gray is None:
            self.to_grayscale()
        self.processed = cv2.GaussianBlur(self.gray, (kernel_size, kernel_size), 0)
        self.debug_images["noise_reduced"] = self.processed
        logger.debug("Noise reduced (kernel=%d)", kernel_size)
        return self.processed

    def enhance_contrast(self):
        """Enhance contrast using CLAHE."""
        if self.gray is None:
            self.to_grayscale()
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.processed = clahe.apply(self.gray)
        self.debug_images["contrast_enhanced"] = self.processed
        logger.debug("Contrast enhanced")
        return self.processed

    def threshold(self, method="otsu", block_size=11, c=2):
        """Apply thresholding."""
        if self.gray is None:
            self.to_grayscale()

        if method == "otsu":
            _, thresh = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        elif method == "adaptive":
            thresh = cv2.adaptiveThreshold(
                self.gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, c
            )
        elif method == "binary":
            _, thresh = cv2.threshold(self.gray, 127, 255, cv2.THRESH_BINARY_INV)
        else:
            raise ValueError(f"Unknown threshold method: {method}")

        self.processed = thresh
        self.debug_images["threshold"] = self.processed
        logger.debug("Threshold applied (%s)", method)
        return self.processed

    def deskew(self):
        """Detect and correct sheet rotation using Hough line detection."""
        if self.original is None:
            raise ValueError("No image loaded")

        gray = self.gray if self.gray is not None else self.to_grayscale()
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            logger.warning("No lines detected for deskewing")
            return self.original

        angles = []
        for line in lines[:50]:
            _, theta = line[0]
            if np.pi / 4 < theta < 3 * np.pi / 4:
                angles.append(np.degrees(theta) - 90)

        if not angles:
            logger.warning("Could not determine rotation angle")
            return self.original

        median_angle = np.median(angles)
        if abs(median_angle) < 0.5:
            logger.debug("Image is straight (angle: %.2f)", median_angle)
            return self.original

        h, w = self.original.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        deskewed = cv2.warpAffine(
            self.original, rotation_matrix, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
        )

        self.original = deskewed
        if self.gray is not None:
            self.gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)

        logger.info("Deskewed: rotated %.2f degrees", median_angle)
        self.debug_images["deskewed"] = deskewed
        return deskewed

    def auto_crop(self):
        """Automatically detect and crop the exam area."""
        if self.original is None:
            raise ValueError("No image loaded")

        gray = self.gray if self.gray is not None else self.to_grayscale()
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            logger.warning("No contours found for auto-crop")
            return self.original

        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        img_area = self.original.shape[0] * self.original.shape[1]

        if w * h < img_area * 0.5:
            logger.warning("Detected area too small, keeping original")
            return self.original

        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(self.original.shape[1] - x, w + 2 * margin)
        h = min(self.original.shape[0] - y, h + 2 * margin)

        self.original = self.original[y : y + h, x : x + w]
        if self.gray is not None:
            self.gray = self.gray[y : y + h, x : x + w]
        if self.processed is not None:
            self.processed = self.processed[y : y + h, x : x + w]

        logger.info("Auto-cropped: %dx%d at (%d, %d)", w, h, x, y)
        self.debug_images["auto_cropped"] = self.original
        return self.original

    def full_preprocess(self, deskew=True, auto_crop=True):
        """Apply full preprocessing pipeline."""
        logger.info("Starting preprocessing pipeline")

        if deskew:
            self.deskew()
        if auto_crop:
            self.auto_crop()

        self.to_grayscale()
        self.reduce_noise(kernel_size=5)
        self.enhance_contrast()
        self.threshold(method="otsu")

        logger.info("Preprocessing complete")
        return self.processed

    def save_debug_images(self, output_dir):
        """Save all intermediate images for inspection."""
        os.makedirs(output_dir, exist_ok=True)
        images = {
            "01_original": self.original,
            "02_grayscale": self.gray,
            "03_processed": self.processed,
        }
        images.update({f"04_{k}": v for k, v in self.debug_images.items()})

        for name, img in images.items():
            if img is not None:
                filepath = os.path.join(output_dir, f"{name}.png")
                cv2.imwrite(filepath, img)
                logger.debug("Saved debug image: %s", filepath)
