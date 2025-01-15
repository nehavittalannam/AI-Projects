PDF_doc_extraction.py

Dependencies The following Python libraries are required to run this script:

PyPDF
pytesseract
Pillow (PIL)
PyMuPDF (fitz)
pdfplumber
You can install these dependencies using pip:

code pip install PyPDF2 pytesseract Pillow pymupdf pdfplumber

Additionally, ensure that Tesseract OCR is installed on your system. You can find installation instructions here. Refer: https://github.com/tesseract-ocr/tesseract

Overview This Python script, document_extraction.py, enables users to extract text, images, and tables from PDF documents. The extracted content will be saved in specified output directories, allowing for further analysis or processing. The script provides the following features:

Text Extraction: Extracts text content from PDF pages.
Image Extraction: Extracts images embedded in the PDF and saves them to a specified directory.
OCR for Images: Uses Tesseract OCR to extract text from images.
Table Extraction: Extracts tables from PDF pages and prints their contents.
How to Run the Application Setup: Ensure you have installed the required dependencies and Tesseract OCR on your machine.

Prepare Input: Place the PDF file you wish to process in an accessible directory.

Update Script:

Modify the script by entering the appropriate paths:
Set pdf_file_path to the path of your PDF file.
Set output_directory to the path where you want to save extracted images.
Specify the path to the Tesseract executable in pytesseract.pytesseract.tesseract_cmd.
Run the Script: Execute the script using Python:
code:python document_extraction.py

Output: The extracted text will be saved to output.txt. Extracted images will be saved in the specified output directory. Extracted tables will be printed to the console.

This documentation should help users understand the requirements, functionality, and usage of your document extraction script.
