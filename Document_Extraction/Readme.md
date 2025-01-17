**Document Splitter, Image Extractor, and Analyzer**

This Python script splits DOCX files into sections based on Heading1 styles, extracts images from the pages, and analyzes both text and images using OpenAI’s Azure API. It then embeds the extracted data and indexes it into Elasticsearch.

**Features**

Split DOCX by Heading1 styles.
Extract images from DOCX and save as PNG.
Analyze text and images with OpenAI's language model.
Embed and index data in Elasticsearch.
Requirements

**Python 3.x**

Libraries: spire.doc, aspose-words, openai, elasticsearch

**Install dependencies:**

pip install spire.doc aspose-words openai elasticsearch

**Setup**

Set your Azure OpenAI credentials (api_key, endpoint, api_version). Set your Elasticsearch credentials (username, password, host_name).

**Usage**

Run the script and input the following when prompted: File Name: DOCX file name. Source File Path: Path to the DOCX file. Output Folder Path: Directory for storing the split documents and images.

**The script will:**

Split the document by Heading1. 
Save images as PNG files.
Analyze the text and images using OpenAI’s API.
Embed and index the data in Elasticsearch.
