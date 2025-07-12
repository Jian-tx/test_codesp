from chromadb import Client

client = Client(persist_directory=persist_directory)
print(client.list_collections())
