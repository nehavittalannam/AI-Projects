import easyocr
import cv2
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your_api_key",  
    api_version="your_api_version",
    azure_endpoint="your_api_endpoint"
)
# Function to extract text using easyOCR
def extract_text_from_image(image_path):
    # Create an easyOCR reader instance
    reader = easyocr.Reader(['en'])  # We specify 'en' for English language

    # Read the image using OpenCV (just to visualize if needed)
    img = cv2.imread(image_path)
    
    # Use EasyOCR to extract text
    result = reader.readtext(image_path, detail=0, width_ths=0.9)    
    return result

# Path to your Aadhaar/PAN card image
image_paths = ["path_to_aadhar_card_1.jpg", "path_to_aadhar_card_2.jpg", "path_to_aadhar_card_3.jpg"]  # Replace with the actual image paths

for image_path in image_paths:
    extracted_text = extract_text_from_image(image_path)
    print(extracted_text)
    response = client.chat.completions.create(
            model="gpt-35-turbo",  # model = "deployment_name".
            messages=[
                {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                {"role": "user", "content": f'''There will be two types of documents you may encounter:
                1. **Aadhaar Card**
                2. **PAN Card**
                Please carefully follow the guidelines below based on the type of document. The content provided to you will be extracted text from the image of the document. Use the following instructions based on the type of document.
                    ### If the extracted text is from an **Aadhaar Card**:
                    - **Extract the following fields**:
                    - **Name**: The full name of the individual.
                    - **Date of Birth**: The full date of birth (day, month, year). If only the year is present, provide only the year. Do not infer or assume any details.
                    - **Sex (Gender)**: The gender of the individual (Male/Female/Other).
                    - **Address**: The address associated with the Aadhaar card.
                    - **Aadhaar Number**: The 12-digit Aadhaar number.
                
                    - **Instructions for missing or unclear data**:
                    - If any of the required fields (Name, Date of Birth, Sex, Address, Aadhaar Number) are not found in the text, return **“Data not found”** for that specific field.
                    - If the **Date of Birth** only contains the year (e.g., "1990"), return only the year and **do not infer** the day or month.
                    - If the full Date of Birth is present with day, month, and year (e.g., "01 January 1990"), return the entire date as it is.
                    - Do not include any extra details, assumptions, or explanations. Just return the exact details in the required format.
    
                    **Output format**:
                    Provide the details in the following format:
                    - **Name**: [Extracted Name]
                    - **DOB**: [Extracted Date of Birth]
                    - **Gender**: [Extracted Gender]
                    - **Address**: [Extracted Address]
                    - **Aadhaar Number**: [Extracted Aadhaar Number]
                Do not include any unnecessary information or assumptions, and only provide the details as per the fields mentioned.
                ### If the extracted text is from a **PAN Card**:
                - **Extract the following fields**:
                - **Name**: The full name of the individual (as printed on the PAN card).
                - **Father’s Name**: The name of the father as printed on the PAN card.
                - **Date of Birth**: The full date of birth (day, month, year). If only the year is present, return only the year.
                - **PAN Number**: The 10-character Permanent Account Number (PAN) which typically follows a pattern: [A-Z]{5}[0-9]{4}[A-Z]{1}.
            
    
                - **Instructions for missing or unclear data**:
                - If any of the required fields (Name, Father’s Name, Date of Birth, PAN Number) are not found in the text, return **“Data not found”** for that field.
                - If the **Date of Birth** only contains the year (e.g., "1990"), provide only the year, not the full date.
                - If the full Date of Birth is available (e.g., "01 January 1990"), provide the entire date.
    
                **Output format**:
                Provide the details in the following format:
                - **Name**: [Extracted Name]
                - **Father’s Name**: [Extracted Father’s Name]
                - **DOB**: [Extracted Date of Birth]
                - **PAN Number**: [Extracted PAN Number]
            PLEASE DONT INCLUDE ANY KIND OF NOTE OR EXPLANATION OR INTRODUCTION , JUST DETAILS IS ENOUGH
                PLEASE JUST GIVE THE DETAILS. DONOT INCLUDE UNNECESSARY TEXT , INSTRUCTIONS OR REASONING:
            HERE IS THE EXTRACTED TEXT :{extracted_text}
    '''}
            ]
        )
    
        # Print the response from OpenAI
    print("\nOpenAI Response:")
    print(response.choices[0].message.content)
    print("****************"*5)
