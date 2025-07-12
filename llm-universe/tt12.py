import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from tt11 import split_docs

# 加载 .env 文件
load_dotenv()

# 从环境变量获取配置
api_key = os.getenv("OPENAI_API_KEY")
base_url = "https://xiaoai.plus/v1"
model = "text-embedding-3-small"

# 配置 OpenAI Embedding
embedding = OpenAIEmbeddings(
    api_key=api_key,
    base_url=base_url,
    model=model
)

# 设置向量数据库持久化路径
persist_directory = 'llm-universe/data_base/vector_db'

# 创建 Chroma 向量库
vectordb = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory=persist_directory
)

# 输出当前向量数量
print(f"向量库中存储的数量：{vectordb._collection.count()}")

question="什么是大语言模型"
mmr_docs = vectordb.max_marginal_relevance_search(question,k=3)
for i, sim_doc in enumerate(mmr_docs):
    print(f"MMR 检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")
