from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import shutil
import os
import json
import pdfplumber
from bs4 import BeautifulSoup

app = FastAPI()

# Define the correct upload directory inside WSL
UPLOAD_DIR = "/mnt/c/Users/arora/projects/ROE/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "FastAPI Server is Running"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles file uploads and saves them in the upload directory."""
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "location": file_location}

def load_file(file_path):
    """Loads a file based on its format and converts it to a Pandas DataFrame."""
    try:
        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # If JSON is a dictionary of lists, convert properly
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame.from_dict(data, orient="index")
            else:
                raise ValueError("Unsupported JSON format")

        elif file_path.endswith(".csv"):
            return pd.read_csv(file_path)

        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)

        elif file_path.endswith(".html"):
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            table = soup.find("table")
            if table is None:
                raise ValueError("No table found in HTML")
            return pd.read_html(str(table))[0]  # Convert HTML table to DataFrame

        elif file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                tables = [pd.DataFrame(table) for page in pdf.pages for table in page.extract_tables()]

            if not tables:
                raise ValueError("No tables found in PDF")

            return pd.concat(tables, ignore_index=True)  # Combine all tables into one DataFrame

        else:
            raise ValueError("Unsupported file format")

    except Exception as e:
        raise ValueError(f"Error processing file {file_path}: {str(e)}")

@app.get("/eda/{filename}")
def perform_eda(filename: str):
    """Performs Exploratory Data Analysis (EDA) on an uploaded file."""
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = load_file(file_path)

        if df.empty:
            raise ValueError("Extracted table is empty")

        stats = {
            "shape": df.shape,
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "summary": df.describe(include="all").to_dict()
        }

        return stats
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
