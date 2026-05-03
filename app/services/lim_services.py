#新增檔案
import requests


def generate_answer(question: str,contexts: list[str]):
    #把chunk串起來
    context_text = "\n".join(contexts)

    prompt = f"""
你是一個專業的文件問答助手。

請「只根據提供的內容找尋相關內容」回答問題，不要自行推測。

請遵守以下規則：
1. 用「繁體中文」回答
2. 不要加入額外問題
3. 不要自己補充不存在的資訊
4. 如果內容中沒有答案，請回答：「文件中沒有相關資訊」

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