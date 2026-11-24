#pip install python-docx
#pip install --upgrade pip
#pip install beautifulsoup4
#pip install requests
#pip install langchain
# This script reads URLs from a text file, fetches the HTML content of each URL, extracts and cleans the text, and then saves it to a .docx file. Each .docx file is named after the last segment of the URL. Make sure to have the required libraries installed before running the script.

from urllib.parse import urlparse
import requests
from langchain.docstore.document import Document

file_path = 'pages_name.txt'  


lists=[]
with open(file_path, 'r') as file:
    for line in file:
        url = line.strip()  
        lists.append(url)
        
print(lists)

from bs4 import BeautifulSoup
import re
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def fetch_webpage(url):
    response = requests.get(url)
    return response.text

def clean_text(text):
    # Remove extra whitespace and newlines
    text = ' '.join(text.split())
    # Remove any remaining unwanted characters or patterns (example: URLs, special characters)
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"]+', '', text)  # Remove special characters except punctuation
    return text

from docx import Document

def write_to_docx(text_content, output_filename):
    doc = Document()  # Create a new Document object

    # Add a heading
    doc.add_heading('Document Title', level=1)

    doc.add_paragraph(text_content)

    # Save the document
    doc.save(output_filename)

for url in lists:
        html_content=fetch_webpage(url)
        page_text=parse_html(html_content)
        final_text=clean_text(page_text)
        output_filename=url.split('/')[-1]+'.docx'

        write_to_docx(final_text,output_filename)

if __name__ == "__main__":
    pass