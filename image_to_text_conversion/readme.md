Image-to-Text Conversion in DOCX Files Using OpenAI
This project automates the process of extracting images from a Microsoft Word (.docx) document and replacing them with generated image summaries using an OpenAI-powered language model (LLM). The solution integrates with Azure OpenAI, extracts image data from DOCX files, and generates textual descriptions for the images.

Features
Extracts images from .docx files.
Generates image captions and summaries using a pre-configured OpenAI model.
Replaces images with their summaries in the DOCX file.
Saves images to a folder and organizes them by index.
Integrates with Azure OpenAI API for image summarization.
Requirements
Before running the project, you need to set up the following:

Python 3.x (preferably 3.6 or higher)
Libraries:
python-docx
requests
openai
python-dotenv
base64
os
You can install the required libraries using pip:

bash
Copy
pip install python-docx requests openai python-dotenv
Setup
Clone the repository:
bash
Copy
git clone https://github.com/your-username/repository-name.git
cd repository-name
Create a .env file in the root directory of the project to store your Azure API credentials. The .env file should include the following variables:
env
Copy
AZURE_API_KEY=your_api_key
AZURE_API_BASE=your_api_base
AZURE_API_VERSION=your_api_version
Replace your_api_key, your_api_base, and your_api_version with your Azure OpenAI API credentials.

Ensure the images folder exists by running the code, which will automatically create the folder if it doesn’t exist. The images will be saved to this folder during the extraction process.
Code Overview
1. ensure_images_folder(folder_name)
Creates a folder named images to store the extracted images. This ensures that the folder is present before saving the images.

2. save_image(image_bytes, image_index, folder_name)
Saves the image bytes to disk with a unique name based on the index, e.g., image_1.jpg, image_2.jpg, etc.

3. get_image_summary(image_bytes, llm)
This function takes the image bytes, converts it to Base64, and sends it to an OpenAI model for summarization. The model is instructed to return a caption and description for the image.

4. get_images(doc)
Extracts and saves images from the given DOCX file. The images are stored in the images folder.

5. replace_images_with_text(doc_path, output_path)
This function takes the input DOCX file (doc_path), extracts the images, and replaces them with the generated summaries. The resulting document is saved to output_path.

Example Usage
Prepare your DOCX file:

Make sure that the DOCX file you want to process contains images.
Run the script to extract images and replace them with summaries:

python
Copy
replace_images_with_text("input_doc.docx", "output_doc.docx")
This command will extract the images from input_doc.docx, replace them with the generated summaries, and save the modified document as output_doc.docx.

Environment Setup
Create a .env file to store your API keys and configuration details for Azure OpenAI. Here’s an example of the required configuration:

env
Copy
AZURE_API_KEY=your_api_key
AZURE_API_BASE=your_api_base
AZURE_API_VERSION=your_api_version
Important:
You must replace the placeholders with actual values from your Azure OpenAI setup.
Ensure your model and API version are correctly specified when calling the API.
