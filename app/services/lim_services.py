#新增檔案
import requests


def generate_answer(question: str,contexts: list[str]):
    #把chunk串起來
    context_text = "\n".join(contexts)

    prompt = f"""
你是一個專業的文件問答助手。

請「直接從內容中找出答案並完整引用原文」，不要改寫、不要摘要。


請嚴格遵守：
1. 一律使用「繁體中文」回答
2. 不可以使用英文
3. 直接引用或整理文件內容
4. 不要翻譯成英文

內容:{context_text}

問題:{question}

請用清楚的方式回答
"""
     # 3️⃣ 呼叫 Ollama API
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()

    return result["response"]