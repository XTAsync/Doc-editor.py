# Document Image Editor

A Streamlit tool for extracting text from document images and making visual edits to selected regions.

## Features

- Upload PNG and JPEG document images
- Extract text with optical character recognition (OCR)
- Identify common fields such as names, dates, and amounts
- Select image regions and overlay replacement text
- Preview and download edited images

## Technology

Python · Streamlit · Tesseract OCR · OpenCV · Pillow · NumPy

## Run Locally

Install the Tesseract OCR engine for your operating system, then install the Python dependencies:

```bash
pip install streamlit pytesseract opencv-python numpy pillow streamlit-drawable-canvas
streamlit run de.py
```

## Notes

OCR results may require manual correction. The editor produces an altered image; it does not modify or verify the original source document.
