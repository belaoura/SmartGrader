# SmartGrader APP With PDF Export

This is a modified version of SmartGrader that generates both HTML and PDF versions of exam sheets.

## What's New

When you generate an exam sheet, the system now creates:
- **HTML file** - For viewing in browser
- **PDF file** - For printing directly

## Installation

### 1. Install pdfkit for PDF generation:

```bash
pip install pdfkit
```

### 2. Download and install wkhtmltopdf:

Go to: https://wkhtmltopdf.org/downloads.html
Download the Windows installer (.exe)

### 3. Other dependencies (if not already installed):

```bash
pip install opencv-python numpy PyQt5 Pillow qrcode pyzbar
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Click "Generate Answer Sheet"
3. Select an exam
4. The system will generate BOTH files:
   - `qcm_exam_X_final.html` (view in browser)
   - `qcm_exam_X_final.pdf` (print this!)

## Troubleshooting

### PDF not generating?
1. Make sure pdfkit is installed: `pip install pdfkit`
2. Make sure wkhtmltopdf is installed: https://wkhtmltopdf.org/downloads.html
3. Check console for error messages

### Alternative: Print from HTML
If PDF fails, open the HTML file in your browser and press Ctrl+P to print directly.

## Files Modified

- `generate_qcm_sheet.py` - Added PDF generation using pdfkit + wkhtmltopdf
- `main.py` - Updated to handle both HTML and PDF outputs
