import os
from docling.document_converter import DocumentConverter
from docx import Document
 
# Define the source file path
source = "your_source_path"  # The path of the source document
 
# Initialize the DocumentConverter
converter = DocumentConverter()
 
# Convert the source document
result = converter.convert(source)
 
# Export the converted content to markdown
markdown_content = result.document.export_to_markdown()
 
# Define the path to save the new .docx file
output_directory = "Document_extracted2"
output_path = os.path.join(output_directory, "Converted_doc.docx")
 
# Check if the directory exists, and create it if not
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
 
# Create a new .docx file and add the markdown content into it
doc = Document()
doc.add_paragraph(markdown_content)
 
# Save the new document
doc.save(output_path)
 
print(f"Converted document saved as: {output_path}")
 
