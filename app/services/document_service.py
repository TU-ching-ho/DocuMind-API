from pypdf import PdfReader
import docx
import re

def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text +=page.extract_text() or ""
    return text

def reaf_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def split_by_sentence(text: str):
    sentences = re.split(r"[。！？\n]", text)
    return [s.strip() for s in sentences if s.strip()]

'''
def chunk_text(text: str, chunk_size = 200, overlap = 50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap
    return chunks
'''
def build_chunks(sentences, chunk_size=200, overlap=50):
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())

            # overlap（保留上下文）
            current_chunk = current_chunk[-overlap:] + sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def remove_toc_lines(text: str) -> str:
    lines = text.split("\n")

    filtered = []
    for line in lines:
        # 過濾「......」目錄行
        if re.search(r"\.{3,}", line):
            continue
        filtered.append(line)

    return "\n".join(filtered)

def clean_text(text: str) -> str:
    #移除null字元
    text = text.replace("\x00","")

    #移除符號 ex:.....
    text = re.sub(r"\{2,}"," ",text)

    #移除「點點 + 空白」的組合
    text = re.sub(r"(\.\s*){2,}", " ", text)

    #移除「數字目錄格式」（例如 1 2 3）
    text = re.sub(r"\s\d+\s", " ", text)

    #移除空白
    text = re.sub(r"\s+"," ",text)

    #移除控制字元
    text = "".join(c for c in text if c.isprintable())

     # 移除 null 字元
    text = text.replace("\x00", "")

    # 移除奇怪控制字元
    text = "".join(c for c in text if c.isprintable())

    text = remove_toc_lines(text)

    return text.strip()