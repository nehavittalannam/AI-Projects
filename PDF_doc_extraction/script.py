from PyPDF2 import PdfReader
import re
import requests
import pytesseract
from PIL import Image
import io
import hashlib
import fitz
import pdfplumber

# Provide the path to your PDF file
pdf_file_path = "{enter your PDF file path}"

# Extracting the text using PyPDF2
def extract_pdf_content(filename):
    content = ""
    with open(filename, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            extracted_text = page.extract_text()
            cleaned_text = re.sub(r'\s+', ' ', extracted_text).strip()
            content += cleaned_text + '\n'
    return content

# Extract the content from the PDF
pdf_content = extract_pdf_content(pdf_file_path)

# Save the extracted content to a text file
with open("output.txt", "w", encoding='UTF8') as file:
    file.write(pdf_content)

print("Successfully extracted the text content from the file.")

# Extracting images using PyMuPDF
def is_blank_image(image):
    grayscale_image = image.convert("L")
    histogram = grayscale_image.histogram()
    return max(histogram) == sum(histogram)

def is_icon_image(image, min_width=50, min_height=50):
    width, height = image.size
    return width < min_width and height < min_height

def get_image_hash(image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    return hashlib.md5(image_bytes.getvalue()).hexdigest()

def extract_images_from_pdf(pdf_path, output_folder):
    pdf_document = fitz.open(pdf_path)
    seen_hashes = set()
    image_count = 0
    image_paths = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            image_hash = get_image_hash(image)
            if image_hash not in seen_hashes and not is_blank_image(image) and not is_icon_image(image):
                seen_hashes.add(image_hash)
                image_path = f"{output_folder}/page_{page_num+1}_img_{img_index}.{image_ext}"
                image.save(image_path)
                image_count += 1
                image_paths.append(image_path)
    print(f"Total extracted images: {image_count}")
    return image_paths

def extract_text_from_image(image_path):
    try:
        # Specify the path to the Tesseract executable
        pytesseract.pytesseract.tesseract_cmd = '{enter path to Tesseract executable}'
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}")
        return None

output_directory = "{enter your output directory path}"

image_paths = extract_images_from_pdf(pdf_file_path, output_directory)

for image_path in image_paths:
    text = extract_text_from_image(image_path)
    if text:
        print(f"Extracted text from {image_path}: {text}")
        print("------------------" * 5)

# Extracting tables using pdfplumber
def extract_tables_from_pdf(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        extracted_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            extracted_tables.extend(tables)
    
    cleaned_tables = []
    for table in extracted_tables:
        cleaned_table = []
        for row in table:
            cleaned_row = [cell.replace('\n', ',') if cell is not None else '' for cell in row]
            cleaned_table.append(cleaned_row)
        cleaned_tables.append(cleaned_table)
    
    return cleaned_tables

extracted_tables = extract_tables_from_pdf(pdf_file_path)

# Print the extracted tables
for index, table in enumerate(extracted_tables):
    print(f"Table {index+1}:")
    for row in table:
        print(row)
    print("------------------" * 5)
