# #pip install python-docx
# #pip install --upgrade pip
# #pip install beautifulsoup4
# #pip install requests
# #pip install langchain
# # This script reads URLs from a text file, fetches the HTML content of each URL, extracts and cleans the text, and then saves it to a .docx file. Each .docx file is named after the last segment of the URL. Make sure to have the required libraries installed before running the script.

# from urllib.parse import urlparse
# import requests
# #from langchain.docstore.document import Document
# from langchain_core.documents import Document


# file_path = 'pages_name.txt'  


# lists=[]
# with open(file_path, 'r') as file:
#     for line in file:
#         url = line.strip()  
#         lists.append(url)
        
# print(lists)

# from bs4 import BeautifulSoup
# import re
# def parse_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     return soup.get_text()

# def fetch_webpage(url):
#     response = requests.get(url)
#     return response.text

# def clean_text(text):
#     # Remove extra whitespace and newlines
#     text = ' '.join(text.split())
#     # Remove any remaining unwanted characters or patterns (example: URLs, special characters)
#     text = re.sub(r'http\S+', '', text)  # Remove URLs
#     text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"]+', '', text)  # Remove special characters except punctuation
#     return text

# from docx import Document

# def write_to_docx(text_content, output_filename):
#     doc = Document()  # Create a new Document object

#     # Add a heading
#     doc.add_heading('Document Title', level=1)

#     doc.add_paragraph(text_content)

#     # Save the document
#     doc.save(output_filename)

# for url in lists:
#         html_content=fetch_webpage(url)
#         page_text=parse_html(html_content)
#         final_text=clean_text(page_text)
#         output_filename=url.split('/')[-1]+'.docx'

#         write_to_docx(final_text,output_filename)



# Required installs:
# pip install python-docx beautifulsoup4 requests

import os
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from docx import Document


# =========================
# READ URLS FROM FILE
# =========================
file_path = 'pages_name.txt'

urls = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        url = line.strip()
        if url:
            urls.append(url)

print(f"Loaded {len(urls)} URLs")


# =========================
# FETCH WEBPAGE
# =========================
def fetch_webpage(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None


# =========================
# PARSE HTML (CLEAN TEXT)
# =========================
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.extract()

    text = soup.get_text(separator=" ")
    return text


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    text = ' '.join(text.split())  # remove extra whitespace
    text = re.sub(r'http\S+', '', text)  # remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]+', '', text)  # clean special chars
    return text


# =========================
# GENERATE SAFE FILENAME
# =========================
def generate_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        return "homepage.docx"

    # Replace slashes with underscore
    filename = path.replace("/", "_")

    # Remove invalid filename characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)

    return filename + ".docx"


# =========================
# WRITE TO DOCX
# =========================
def write_to_docx(text_content, output_filename):
    try:
        doc = Document()

        # Add title
        doc.add_heading(output_filename.replace(".docx", ""), level=1)

        doc.add_paragraph(text_content)

        doc.save(output_filename)

    except Exception as e:
        print(f"❌ Error saving {output_filename}: {e}")


# =========================
# MAIN PROCESS
# =========================
output_folder = "scraped_docs"
os.makedirs(output_folder, exist_ok=True)

for url in urls:
    print(f"\n🔍 Processing: {url}")

    html_content = fetch_webpage(url)
    if not html_content:
        continue

    page_text = parse_html(html_content)
    final_text = clean_text(page_text)

    if not final_text.strip():
        print("⚠️ Empty content, skipping...")
        continue

    filename = generate_filename(url)
    filepath = os.path.join(output_folder, filename)

    write_to_docx(final_text, filepath)

    print(f"✅ Saved: {filepath}")


print("\n🎉 DONE: All pages processed successfully!")