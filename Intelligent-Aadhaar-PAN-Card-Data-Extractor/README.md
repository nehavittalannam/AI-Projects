# Intelligent Aadhaar & PAN Card Data Extractor

**OCR + Azure OpenAI Powered Document Parsing System**

An AI-powered document processing system that extracts structured information from **Aadhaar** and **PAN** card images using **EasyOCR** and **Azure OpenAI (GPT-3.5 Turbo)**.

This project automates identity document parsing and converts unstructured OCR text into structured JSON-like output with high accuracy and strict validation rules.


##  Project Overview

This system:

* Reads Aadhaar & PAN card images
* Extracts raw text using OCR
* Uses Azure OpenAI to intelligently identify document type
* Structures and validates extracted fields
* Handles missing or partial data gracefully


### Components Used:

* **OCR Engine:** `easyocr`
* **Image Processing:** `opencv-python`
* **LLM Processing:** Azure OpenAI (`gpt-35-turbo`)
* **Language:** Python 3.x


## 📂 Supported Document Types

### 1️⃣ Aadhaar Card

Extracted Fields:

* Name
* Date of Birth (Full date or Year only)
* Gender
* Address
* Aadhaar Number (12-digit)


### 2️⃣ PAN Card

Extracted Fields:

* Name
* Father’s Name
* Date of Birth
* PAN Number (Format: `ABCDE1234F`)


## 🎯 Key Features

* Automatic document type detection
* Strict field-level extraction rules
* No assumptions for missing data
* Smart DOB handling (year-only vs full date)
* Clean structured output format
* Batch image processing support
* Azure OpenAI integration


## 🛠️ Installation

```bash
pip install easyocr
pip install opencv-python
pip install openai
```


## 🔑 Configuration

Update your Azure OpenAI credentials:

```python
client = AzureOpenAI(
    api_key="your_api_key",
    api_version="your_api_version",
    azure_endpoint="your_api_endpoint"
)
```

Make sure you have deployed:

* `gpt-35-turbo` (Azure deployment name)


## ▶️ How to Run

1. Add image paths inside:

```python
image_paths = [
    "path_to_aadhar_card_1.jpg",
    "path_to_aadhar_card_2.jpg"
]
```

2. Run:

```bash
python main.py
```

3. Output will be displayed in structured format.

## 💡 Use Cases

* eKYC Automation
* Banking & FinTech Verification
* HR Document Processing
* Identity Validation Systems
* Digital Onboarding Workflows


## 🧠 Tech Stack

* Python
* EasyOCR
* OpenCV
* Azure OpenAI
* GPT-3.5 Turbo
* Prompt Engineering



**Neha V Annam**
AI & Data Engineer

