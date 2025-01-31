import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
import logging
import os
from elasticsearch import Elasticsearch
import re

# Suppress SSL/TLS related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logfilepath = "MetaData2.log"
logging.basicConfig(filename=logfilepath, level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')

# Global variable to maintain URL count
count = 0

# Proxy information
proxy_address = os.getenv('PROXY_ADDRESS')  # Use environment variable for proxy
proxies = {
    "http": proxy_address,
    "https": proxy_address
}

# Initialize visited URLs set
visited_urls = set()

# Elasticsearch connection setup
def connection(username, password):
    server_ip = ['10.68.191.97', '10.68.191.91', '10.68.191.99', '10.68.191.135', '10.68.191.101']
    for server in server_ip:
        url = f"http://{username}:{password}@{server}:9200"
        es = Elasticsearch([url], request_timeout=60)
        if es.ping():
            logging.info('Elastic search successful: ' + str(es))
            return es

# Token generation for embedding
def token_generation():
    try:
        url = os.getenv('TOKEN_URL')  # Environment variable for token URL
        appid = os.getenv('APP_ID')   # Use environment variable for appid
        type1 = "user"
        json_input = {"AppID": appid, "type": type1}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, json=json_input, headers=headers)
        response.raise_for_status()
        out = response.json()
        logging.info("Bearer token generated")
        return out['access_token']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while generating token: {e}")
        return None

# Encoder function for embedding content
def encoder(text, token):
    try:
        EmbedUrl = os.getenv('EMBED_URL')  # Use environment variable for Embed URL
        json_data = {"text": text}
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }
        response = requests.post(url=EmbedUrl, json=json_data, headers=headers)
        out = response.json()
        return out['embedding']
    except Exception as Encoding:
        logging.error(f"Error while Embedding data: {Encoding}")
        raise Exception(f'Error while Embedding data: {Encoding}')

# Clean the extracted content
def clean_content(content):
    cleaned_content = "\n".join(line.strip() for line in content.splitlines() if line.strip())
    return cleaned_content

# Chunk the content to make it more manageable for storage
def chunk_content(content, chunk_size=1000):
    words = content.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Process and store content in Elasticsearch
def store_content_in_elasticsearch(url, data, token, es):
    encode_data = encoder(data, token)
    index_to_store = "[put-index-name]"
    doc = {
        'url': url,
        'url_content': data,
        'url_embedded_data': encode_data
    }
    # Use the URL as the document ID to avoid duplicate entries
    response = es.index(index=index_to_store, document=doc, id=url)
    if response:
        logging.info(f"Stored document for URL '{url}' in Elasticsearch.")
    else:
        logging.error(f"Failed to Store document for URL '{url}' in Elasticsearch.")

# Process href links and filter unwanted patterns
def process_href_return_url(href_url, url):
    urls = set()
    unwanted_patterns = [r'#', r'mailto:', r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$']
    for link in href_url:
        url_link = link.get('href')
        url_link = url_link.strip('//')
        # Filter out unwanted links based on patterns
        if any(re.search(pattern, url_link) for pattern in unwanted_patterns):
            continue
        # Resolve relative URLs
        url_link = urljoin(url, url_link)
        # Skip URLs that lead back to the same page or have fragments
        if url_link == url:
            continue
        if url_link.startswith("https:") or url_link.startswith("http:") or url_link.startswith("www.") or ".com" in url_link:
            urls.add(url_link)
    return urls

# Function to extract content from a URL and store it
def extract_url_content(url_link, es, token):
    logging.info(url_link)
    try:
        response = requests.get(url_link, proxies=proxies, verify=False)  # Ensure verify=False is here
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        for data in soup(['style', 'script']):
            data.decompose()
        raw_content = ' '.join(soup.stripped_strings)
        cleaned_content = clean_content(raw_content)
        for chunk in chunk_content(cleaned_content):
            store_content_in_elasticsearch(url_link, chunk, token, es)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception for {url_link}: {e}")
        pass
    except Exception as e:
        logging.error(f"Exception occurred while processing {url_link}: {e}")
        pass

# Recursively process URLs and extract content
def extract_data_recursive(url_link, token, es, depth=0):
    global count
    # Limit the recursion depth to 5
    if depth > 2:
        logging.info(f"Reached maximum recursion depth for URL: {url_link}")
        return

    # Skip the URL if it has already been visited
    if url_link in visited_urls:
        logging.info(f"Skipping already processed URL: {url_link}")
        return

    try:
        # Add the URL to the visited set before processing
        visited_urls.add(url_link)
        
        logging.info(f"Processing URL: {url_link}")
        extract_url_content(url_link, es, token)
        
        # Get nested links from the page and process recursively
        html_content = requests.get(url_link, proxies=proxies, verify=False).content  # Ensure verify=False is here
        soup = BeautifulSoup(html_content, 'html.parser')
        href_url = set(soup.find_all('a', href=True))
        urls = process_href_return_url(href_url, url_link)
        
        # Log count of processed URLs
        count += 1
        logging.info(f"Total processed URLs: {count}")
        
        # Process all the nested URLs recursively with increased depth
        for each_url in urls:
            extract_data_recursive(each_url, token, es, depth+1)
    except Exception as e:
        logging.error(f"Error processing {url_link}: {e}")
        pass

# Main script execution
if __name__ == "__main__":
    urls_list = ["URL_HERE"]
    visited_urls = set()
    token = token_generation()
    es = connection(os.getenv('ES_USERNAME'), os.getenv('ES_PASSWORD'))  # Use environment variables for credentials
    if es and es.ping():
        for url in urls_list:
            extract_data_recursive(url, token, es)
    else:
        logging.error("Unable to connect to Elasticsearch.")
    logging.info(f"Completed parsing the URL")
