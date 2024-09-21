#!/usr/bin/python
import os
import dotenv
import requests
import json
import faiss
from uuid import uuid4
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import JSONLoader
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Load local environment variables
dotenv.load_dotenv()
db_dir = os.getenv("DB_DIR")
faiss_update = os.getenv("FAISS_UPDATE")
openai_token = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("MODEL_NAME")
embeddings_name = os.getenv("EMB_MODEL_NAME")
base_url = os.getenv("BASE_URL")
user_agent = os.getenv("USER_AGENT")

#Remove the existing DB if it exists
if os.path.exists("faiss_db"):
    import shutil
    shutil.rmtree("faiss_db")
 
# Create list of links from index
file_name = 'urls'
file = open(os.path.join(db_dir, file_name), 'r')
Lines = file.readlines()

def sanitize(l):

    while l and l[0] == '\n':
        l.pop(0)

    while l and l[-1] == '\n':
        l.pop()

    result = []
    count = 0
    for i in l:
        if i == '\n':
            count += 1
        else:
            count = 0
        if count < 3:
            result.append(i)

    return result

def parse(html, url):

    title = (html.find('h1') if html.find('h1') is not None else html.find('h2')).get_text().strip()

    example_titles = [(e, e.get_text()) for e in html.find_all('p', 'procedure-heading')]
    example_tabs = [(e.find_next_sibling('div', 'tabs-container'), s) for e, s in example_titles]
    example_tabs_dedup = []

    last = None
    for e, s in example_tabs:
        if e is None:
            continue
        if last == e:
            example_tabs_dedup[-1] = (e, s)
        else:
            example_tabs_dedup.append((e, s))
        last = e
    
    example_tabs = example_tabs_dedup
    examples = sum([[(tab, s) for tab in e.find_all('div', 'tab')] for e, s in example_tabs], [])
    cli_examples = [{"example": e.get_text(), "title": s} for e, s in examples if e.find('p', 'tab-title', string="Command-line interface") is not None]
    panel_examples = [{"example": e.get_text(), "title": s} for e, s in examples if e.find('p', 'tab-title', string="Admin panel") is not None]
    
    lines = sanitize(list(html.strings))
    content = ''.join(lines)
    
    #stripped = [s.strip() for s in content_lines]
    #paragraphs = [s for s in stripped if len(s) > 50 and s.count(' ') > 5 and not any(s in e["example"] for e in cli_examples + panel_examples)]
    paragraphs = []

    return {
        "title": title,
        "content": content,
        "paragraphs": paragraphs,
        "cli_examples": cli_examples,
        "panel_examples": panel_examples,
        "url": url,
    }

json_string = []

headers = {
        "User-Agent": user_agent
    }

def dump_page(page):
    r = requests.get(page, verify=True, headers=headers)
    url = r.url
    #Parse documents from the new doc portal based on Hugo
    if url.startswith('http') and "www.virtuozzo.com/hybrid-infrastructure-docs/" in url:
        content = BeautifulSoup(r.text, 'html.parser').find("div", {"class": "content"})
        soup = (content if content is not None else BeautifulSoup(r.text, 'html.parser'))
    #Parse documents based on the old doc portal based on MadCap
    elif url.startswith('http') and "docs.virtuozzo.com/" in url:
        content = BeautifulSoup(r.text, 'html.parser').find(id='mc-main-content')
        soup = (content if content is not None else BeautifulSoup(r.text, 'html.parser'))
    
    j = parse(soup, url)
    json_string.append(j)
    print(len(json_string))

embeddings = OpenAIEmbeddings(
    openai_api_key=openai_token,
    openai_api_base=base_url,
    model=embeddings_name
    )

index = faiss.IndexFlatL2(len(embeddings.embed_query("Virtuozzo")))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["title"] = record.get("title")
    metadata["content"] = record.get("content")
    metadata["cli_examples"] = record.get("cli_examples")
    metadata["panel_examples"] = record.get("panel_examples")
    metadata["url"] = record.get("url")

    return metadata

def faiss_loader():
    #JSON loader
    loader = JSONLoader(
        file_path='./json/all.json',
        jq_schema='.[]',
        content_key='content',
        metadata_func=metadata_func
        )
    pages = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=400)
    splits = text_splitter.split_documents(pages)
    #Create FAISS DB
    uuids = [str(uuid4()) for _ in range(len(splits))]
    vector_store.add_documents(documents=splits, ids=uuids)
    vector_store.save_local("../faiss_db")
    #Show number of pages
    print(len(pages))

def main():

    if faiss_update == 'Yes':
        i = 0
        for line in Lines:
            dump_page(Lines[i].strip())
            i = i + 1
        with open(f'./json/all.json', "w+") as f:
            json.dump(json_string, f, indent=4)

        faiss_loader()

if __name__ == '__main__':
    main()
