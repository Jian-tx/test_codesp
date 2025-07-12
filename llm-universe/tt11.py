import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

_ = load_dotenv(find_dotenv())

# 获取folder_path下所有文件路径，储存在file_paths里
file_paths = []
folder_path = '/workspaces/test_codesp/llm-universe/data_base/knowledge_db/prompt_engineering'
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_paths.append(file_path)
print(file_paths[:3])

# 遍历文件路径并把实例化的loader存放在loaders里
loaders = []

for file_path in file_paths:
    file_type = file_path.split('.')[-1]
    if file_type == 'pdf':
        loaders.append(PyMuPDFLoader(file_path))
    elif file_type == 'md':
        loaders.append(UnstructuredMarkdownLoader(file_path))

# 下载文件并存储到text
texts = []

for loader in loaders:
    texts.extend(loader.load())

text = texts[1]
print(
    f"每一个元素的类型：{type(text)}.",
    f"该文档的描述性数据：{text.metadata}",
    f"查看该文档的内容:\n{text.page_content[0:]}",
    sep="\n------\n"
)

# 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50)

split_docs = text_splitter.split_documents(texts)

