import chromadb
# 查看数据
# 连接到现有数据库文件夹
client = chromadb.PersistentClient(path="/workspaces/test_codesp/chroma_db")

# 查看所有集合（你创建过的集合名）
collections = client.list_collections()
print("数据库中所有集合：")
for col in collections:
    print(f" - {col.name}")

collection = client.get_collection(name=collections[0].name)

# 查询集合中的所有向量（打印 ID 和 metadata）
results = collection.get(include=['embeddings', 'metadatas', 'documents'])

print("向量数据：")
for i in range(len(results["ids"])):
    print(f"ID: {results['ids'][i]}")
    print(f"Embedding向量: {results['embeddings'][i][:5]}...")  
    print(f"Metadata元数据: {results['metadatas'][i]}")
    print(f"Document文本内容: {results['documents'][i]}")
    print("-" * 40)