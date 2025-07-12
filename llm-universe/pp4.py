from chromadb import Client

# 初始化客户端
client = Client()
collection = client.get_collection("chroma_db") 

# 查找你想要的向量 ID
vector_id = "0c81a1a7-3588-41b9-809b-746da3b03bb2"

# 获取该向量及其内容
result = collection.get(ids=[vector_id])

# 输出向量和原始文本
print("文本：", result["documents"][0])
print("向量：", result["embeddings"][0])
