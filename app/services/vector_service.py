from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

#載入模型
model = SentenceTransformer("all-MiniLM-L6-V2")

def embed_texts(texts: list[str]):
    embeddings = model.encode(texts)
    return np.array(embeddings).astype("float32")

def create_faiss_index(vectors: np.ndarray):
    dim = vectors.shape[1] #向量維度
    index = faiss.IndexFlatL2(dim)  #IndexFlatL2用距離來找最相近
    index.add(vectors)

    return index

def search(index, query: str, chunks: list[str], top_k=3):
    query_vector = embed_texts([query])

    distances, indices = index.search(query_vector, top_k)

    results = [chunks[i] for i in indices[0]]

    print("query:", query)
    print("indices:", indices)

    return results
