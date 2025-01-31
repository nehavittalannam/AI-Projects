# Web Scraper for URL Content Extraction

This project is a web scraper designed to extract content from specified URLs, process the content into embeddings, and store the processed content into an Elasticsearch index.

## Requirements
- Python 3.x
- Install the necessary Python libraries:
    - `requests`
    - `beautifulsoup4`
    - `elasticsearch`
    - `urllib3`
    - `python-dotenv`

## Setup

1. Clone this repository to your local machine.

2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt


3.Create a .env file in the root directory of the project and define your environment variables:

env
Copy
PROXY_ADDRESS=http://your-proxy-address:port
TOKEN_URL=http://your-token-service-url
APP_ID=your-app-id
EMBED_URL=http://your-embedding-service-url
ES_USERNAME=your-elasticsearch-username
ES_PASSWORD=your-elasticsearch-password
Run the script:

bash
Copy
python scraper.py
Logging
The script logs its actions in the MetaData2.log file for debugging and tracking purposes.

License
This project is licensed under the MIT License.

markdown
Copy

### 4. **`.env` Example:**

Create a `.env` file to securely store environment variables:

PROXY_ADDRESS=http://your-proxy-address:port TOKEN_URL=http://your-token-service-url APP_ID=your-app-id EMBED_URL=http://your-embedding-service-url ES_USERNAME=your-elasticsearch-username ES_PASSWORD=your-elasticsearch-password

markdown
Copy

### 5. **requirements.txt**

To create a `requirements.txt`, simply run:

```bash
pip freeze > requirements.txt

