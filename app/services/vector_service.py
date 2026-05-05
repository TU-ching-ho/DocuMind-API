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

def search(index, query: str, chunks: list[str], top_k=5):
    query_vector = embed_texts([query])

    distances, indices = index.search(query_vector, top_k)

    print("query:", query)
    print("indices:", indices)

    return [chunks[i] for i in indices[0] if i < len(chunks)]

def extract_keywords(query: str):
    stopwords = ["的", "是", "有關", "請問", "什麼", "規則"]

    keywords = []

    for ch in query:
        if ch not in stopwords and ch.strip():
            keywords.append(ch)

    return keywords

def rerank(query, candidates):
    keywords = extract_keywords(query)

    scored = []

    for c in candidates:
        score = 0

        # 🔥 keyword 加分
        if any(k in c for k in keywords):
            score += 0.7

        scored.append((c, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [c for c, _ in scored]

def keyword_search(query, chunks):
    keywords = extract_keywords(query)

    results = []

    for c in chunks:
        if any(k in c for k in keywords):
            results.append(c)

    return results

def hybrid_search(query, index, chunks):

    vector_results = search(index, query, chunks, top_k=10)
    keyword_results = keyword_search(query, chunks)

    # 合併
    combined = vector_results + keyword_results

    # 去重
    unique = []
    seen = set()

    for c in combined:
        if c not in seen:
            unique.append(c)
            seen.add(c)

    # 🔥 rerank
    reranked = rerank(query, unique)

    # 👉 最後取前3
    return reranked[:3]

def pick_best_chunk(query, results):
    keywords = extract_keywords(query)

    best = None
    max_hit = 0

    for r in results:
        hit = sum(1 for k in keywords if k in r)

        if hit > max_hit:
            max_hit = hit
            best = r

    return best if best else results[0]