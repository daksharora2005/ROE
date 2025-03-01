from fastapi import FastAPI, UploadFile, File
import pandas as pd
import shutil
import os

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

@app.get("/eda/{filename}")
def perform_eda(filename: str):
    """Performs Exploratory Data Analysis (EDA) on an uploaded CSV file."""
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        df = pd.read_csv(file_path)

        stats = {
            "shape": df.shape,
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "summary": df.describe(include="all").to_dict()
        }

        return stats
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
