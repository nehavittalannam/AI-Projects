import re
import os
from spire.doc import *
from spire.doc.common import *
import aspose.words as aw
import base64
from collections import defaultdict
from openai import AzureOpenAI
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

def sanitize_filename(text):
    return re.sub(r'[<>:"/\\|?*]', '_', text)

file_name=input('enter file name: \n')
source_file_path=input('Enter the source file path: \n')
output_file_path_and_image_path = input("Enter the  path to store the splitted document: \n")

source_document = Document()
source_document.LoadFromFile(source_file_path)

main_filename = os.path.splitext(os.path.basename(source_file_path))[0]

new_documents = []
new_document = None
new_section = None
is_inside_heading = False
heading_text = None

for sec_index in range(source_document.Sections.Count):
    section = source_document.Sections[sec_index]

    for obj_index in range(section.Body.ChildObjects.Count):
        obj = section.Body.ChildObjects[obj_index]
        if isinstance(obj, Paragraph):
            para = obj
            if para.StyleName == "Heading1":
                if new_document is not None:
                    new_documents.append((new_document, heading_text))

                new_document = Document()
                new_section = new_document.AddSection()

                section.CloneSectionPropertiesTo(new_section)
                new_section.Body.ChildObjects.Add(para.Clone())
                heading_text = para.Text.strip()
                is_inside_heading = True
            else:
                if is_inside_heading:
                    new_section.Body.ChildObjects.Add(para.Clone())
        else:
            if is_inside_heading:
                new_section.Body.ChildObjects.Add(obj.Clone())

if new_document is not None:
    new_documents.append((new_document, heading_text))

for i, (doc, heading) in enumerate(new_documents):
    source_document.CloneThemesTo(doc)
    source_document.CloneDefaultStyleTo(doc)

    sanitized_heading = sanitize_filename(heading)
    output_file = f"{output_file_path_and_image_path}\\{file_name}\\split-docs\\{main_filename}_{sanitized_heading}.docx"
    
    doc.SaveToFile(output_file, FileFormat.Docx2016)


folder_path = f"{output_file_path_and_image_path}\\{file_name}\\split-docs"
docx_files = [f for f in os.listdir(folder_path) if f.endswith(".docx")]

for docx_file in docx_files:
    doc = aw.Document(os.path.join(folder_path, docx_file))
    for pageNumber in range(doc.page_count):
        image_options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)
        image_options.jpeg_quality = 100  
        image_options.horizontal_resolution = 300  
        image_options.vertical_resolution = 300  
        extracted_page = doc.extract_pages(pageNumber, 1)  
        output_path=f"{output_file_path_and_image_path}\\{file_name}_images\\{docx_file.replace('.docx', '')}-{pageNumber + 1}_page.png"  
        extracted_page.save(output_path, image_options)



headers = {
    'api-key': 'your_api_key'
}
llm = AzureOpenAI(
    azure_endpoint="your_endpoint",
    api_version="your_api_version",
    default_headers=headers
)

def embedings_creation(text):
    try:
        #your embedding model
        return embeddings
    except Exception as Encoding:
        print(f"Error while Embedding data: {Encoding}")


test_index='Elastic_index'
username = "elastic_user_name"
password = "elasic_password" 
es = Elasticsearch(hosts="host_name", basic_auth=(username, password), timeout=60)
print(es.ping())

def add_to_index(es, actions, timeout=60):
    try:
        bulk(es, actions, request_timeout=timeout, refresh=True)
    except Exception as e:
        raise Exception(f"Bulk indexing failed: {e}") from e

def extraction(images):
    doc_message="""I have a DOCX file that contains text and images. I would like you to help me analyze and summarize the contents of this document in a structured manner. Please follow these guidelines:

            1. Extract the text from the document.
            2. Provide a summary of any images included in the document, explaining their relevance to the extracted text.
            3. Repeat this process for all sections of the document.
            4. Do not provide context which is not present the document
            The document should be divided into clearly defined sections, with text organized into:
            - **Title: **

            - **Text Extracted:**

            - **Image 1 Description:**

            Please analyze this content and provide a structured response following the guidelines above.
            """

    image_messages = []

    for image in images:
        image_url = f"data:image/jpeg;base64,{image}"
        image_messages.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    response = llm.chat.completions.create(
        model="your_model_name", 
        messages=[
            {"role": "system", "content": doc_message},
            {"role": "user", "content": image_messages}
        ]
    )

    text = response.choices[0].message.content
    return text

image_directory = f"{output_file_path_and_image_path}\\{file_name}_images"
image_groups = defaultdict(list)

for filename in os.listdir(image_directory):
    basename = os.path.splitext(filename)[0]
    print(basename)
    prefix = basename.split("-")[0]
    print(prefix)
    filepath = os.path.join(image_directory, filename)
    with open(filepath, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    image_groups[prefix].append(base64_image)

for group, images in image_groups.items():
    print(len(images))
    print(group)
    text=extraction(images)
    print(text)

    embeddings = embedings_creation(text)
    a = {'your_mapping'}
    es.index(index=test_index,body=a)
