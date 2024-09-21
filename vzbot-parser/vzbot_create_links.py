import os
import dotenv
from bs4 import BeautifulSoup
import requests
import json

# Load the configuration from .env
dotenv.load_dotenv()
total_documents_limit = int(os.getenv("TOTAL_DOCUMENTS_LIMIT"))
user_agent = os.getenv("USER_AGENT")
persist_directory = os.getenv("DB_DIR")
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
urls = config.get("urls", [])  # Get the list of URLs from config.json

visited_urls_file = os.path.join(persist_directory, "urls")

#Remove the existing DB if it exists
if os.path.exists(persist_directory):
    import shutil
    shutil.rmtree(persist_directory)

# Create a directory for the DB index
os.makedirs(persist_directory, exist_ok=True)

# Load visited URLs from file
if os.path.exists(visited_urls_file):
    with open(visited_urls_file, 'r') as f:
        visited_urls = set(line.strip() for line in f)
else:
    visited_urls = set()

# Function to save visited URLs to file
def save_visited_urls():
    with open(visited_urls_file, 'w') as f:
        for url in visited_urls:
            f.write(f"{url}\n")

# Function to parse a page and recursively traverse links with limits
def parse_page(url, visited_urls, depth=0, max_depth=5):
    if url in visited_urls or depth > max_depth or len(visited_urls) >= total_documents_limit:
        return
    
    if url.startswith('http') and not url.endswith('.xml'):
        print(url)
        visited_urls.add(url)

    headers = {
        "User-Agent": user_agent
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}: {response.status_code}")
            return
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Search for links and parse them
    # Find links for VHI only 
    for link in soup.find_all('loc'):
        link_url = link.text
        if link_url.startswith('http') and not link_url.endswith('.png') and "docs.virtuozzo.com/virtuozzo_hybrid_infrastructure_6_2" in link_url:
            parse_page(link_url, visited_urls, depth + 1, max_depth)
    # Find links for integration guides
    for link in soup.find_all('loc'):
        link_url = link.text
        if link_url.startswith('http') and not link_url.endswith('.png') and "docs.virtuozzo.com/virtuozzo_integrations_" in link_url:
            parse_page(link_url, visited_urls, depth + 1, max_depth)
    # Find links on the new VHI doc portal
    for link in soup.find_all('a', href=True):
        link_url = link['href']
        if link_url.startswith('http') and "www.virtuozzo.com/hybrid-infrastructure-docs/" in link_url:
            parse_page(link_url, visited_urls, depth + 1, max_depth)

def main():
    # Start parsing for each URL in the configuration
    for url in urls:
        print(url)
        parse_page(url, visited_urls)
        if len(visited_urls) >= total_documents_limit:
            print(f"Total document limit reached: {total_documents_limit}")
            break
    
    save_visited_urls()

    num_documents = len(visited_urls)
    print(f"Index created and saved successfully with {num_documents} documents!")

if __name__ == "__main__":
    main()
