from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from app.services.document_service import reaf_docx,read_pdf,clean_text,build_chunks,split_by_sentence
from app.services.vector_service import embed_texts,create_faiss_index,search,hybrid_search,pick_best_chunk
from app.services.lim_services import generate_answer

app = FastAPI()

UPLOAD_DIR = "uploads"

# 確保資料夾存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

db_chunks = []
db_index = None

class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "DocuMind API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global db_chunks, db_index
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
    
    sentences = split_by_sentence(text)
    
    # chunk
    chunks = build_chunks(sentences)

     # embedding
    vectors = embed_texts(chunks)

     # index
    db_index = create_faiss_index(vectors)

    db_chunks = chunks

    return {
        
        "chunks_count":len(chunks)
         }


@app.post("/ask")
def ask_question(req: QueryRequest):
    if db_index is None or not db_chunks:
            return {
                "error": "No document uploaded yet"
            }

    #results = hybrid_search( req.question,db_index, db_chunks)

    # 1️⃣ 搜尋
    results = search(db_index, req.question, db_chunks)

    # 2️⃣ 丟給本地 AI
    answer = generate_answer(req.question, results)

    # 直接用最相關 chunk
    #best_chunk = pick_best_chunk(req.question, results)

    return {
        "question": req.question,
        "answer": answer, #AI整理
     #   "source_except": best_chunk,
        "sources": results
    }
   