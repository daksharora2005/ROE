from bs4 import BeautifulSoup
import requests
import pandas as pd
import pdfplumber
import json

# Extract tables from an HTML file
def extract_tables_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    tables = pd.read_html(str(soup))
    return tables

# Extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages])

# Extract data from a JSON file
def extract_data_from_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)

