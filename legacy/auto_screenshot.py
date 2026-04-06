"""
Auto Screenshot - Converts HTML to Image
Opens HTML in browser and takes screenshot.
"""

import os
import time
import subprocess
import sys

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not installed. Install with: pip install Pillow")

# ============================================
# 📁 EDIT THIS: Your HTML file name
# ============================================
HTML_FILE = "qcm_exam_3_final.html"
OUTPUT_IMAGE = "sheet_image.png"
# ============================================


def take_screenshot():
    """Open HTML in browser and take screenshot."""
    
    if not PIL_AVAILABLE:
        print("❌ PIL not installed. Run: pip install Pillow")
        return False
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, HTML_FILE)
    
    if not os.path.exists(html_path):
        print(f"❌ HTML file not found: {HTML_FILE}")
        return False
    
    print(f"🌐 Opening: {HTML_FILE}")
    
    # Open HTML in default browser
    if sys.platform == 'win32':
        os.startfile(html_path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', html_path])
    else:
        subprocess.run(['xdg-open', html_path])
    
    print("⏳ Wait 3 seconds for browser to load...")
    time.sleep(3)
    
    # Take screenshot
    print("📸 Taking screenshot...")
    screenshot = ImageGrab.grab()
    screenshot.save(OUTPUT_IMAGE)
    
    print(f"✅ Saved: {OUTPUT_IMAGE}")
    print(f"\n📁 Now edit single_column_scanner.py:")
    print(f"   INPUT_FILE = \"{OUTPUT_IMAGE}\"")
    print(f"\nThen run:")
    print(f"   python single_column_scanner.py")
    
    return True


if __name__ == "__main__":
    if PIL_AVAILABLE:
        take_screenshot()
    else:
        print("\nInstall PIL first:")
        print("pip install Pillow")
