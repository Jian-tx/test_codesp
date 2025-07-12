import os
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. 加载 PDF 
loader = PyMuPDFLoader("/workspaces/test_codesp/JY.pdf")
pdf_pages = loader.load()
print(f"载入后的变量类型为：{type(pdf_pages)}，该 PDF 一共包含 {len(pdf_pages)} 页\n")

# 2. 文本清洗
def clean_text(text):
    pattern = re.compile(r'[^\u4e00-\u9fff](\n)[^\u4e00-\u9fff]', re.DOTALL)
    text = re.sub(pattern, lambda match: match.group(0).replace('\n', ''), text)
    text = text.replace('•', '').replace(' ', '')
    return text

all_text = ""
for i, page in enumerate(pdf_pages):
    cleaned_content = clean_text(page.page_content)
    all_text += cleaned_content + "\n"

print(f"拼接后的文本长度: {len(all_text)}")

#  3. 文本切分
CHUNK_SIZE = 500
OVERLAP_SIZE = 50
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP_SIZE
)

chunks = text_splitter.split_text(all_text)
print(f"分割后文本块数: {len(chunks)}")
print(f"第一块内容预览:\n{chunks[0]}")

# 使用文档分割器对原始 pdf_pages 进行切块（保留元数据）
split_docs = text_splitter.split_documents(pdf_pages)
print(f"切分后的文件数量：{len(split_docs)}")
print(f"切分后的字符数：{sum([len(doc.page_content) for doc in split_docs])}")

#  4. 加载环境变量与 Embedding 配置
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = "https://xiaoai.plus/v1"
model = "text-embedding-3-small"

embedding = OpenAIEmbeddings(
    api_key=api_key,
    base_url=base_url,
    model=model
)

# 5. 存入 Chroma 向量数据库
persist_directory = "/workspaces/test_codesp/chroma_db"
vectordb = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory=persist_directory
)
vectordb.persist()
print(" 向量数据已保存到本地 Chroma 数据库")

# 6. 相似查询示例 
query = "机器学习中的决策树原理是什么？"
results = vectordb.similarity_search(query, k=2)

print("\n【查询结果预览】")
for i, result in enumerate(results):
    print(f"\n第{i+1}个结果:\n{result.page_content}")
