from fastapi import FastAPI, UploadFile, File
import os
from fastapi.responses import JSONResponse
from app.services.document_service import reaf_docx,read_pdf,chunk_text,clean_text

app = FastAPI()

UPLOAD_DIR = "uploads"

# 確保資料夾存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "DocuMind API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    #判斷檔案類型
    if file.filename.endswith(".pdf"):
        text = read_pdf(file_path)
        text = clean_text(text)
    elif file.filename.endswith(".docx"):
        text = reaf_docx(file_path)
        text = clean_text(text)
    else:
        return {"error":"Unsupported file type"}
    
    #chunk
    chunks = chunk_text(text)

    return {
        "filename": file.filename,
        "chunks_count":len(chunks),
        "preview":chunks[3:5] }
        
   