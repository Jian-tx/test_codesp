import re
from langchain_community.document_loaders import PyMuPDFLoader

# 1. 加载 PDF 文件
loader = PyMuPDFLoader("/workspaces/test_codesp/JY.pdf")
pdf_pages = loader.load()

print(f"载入后的变量类型为：{type(pdf_pages)}，该 PDF 一共包含 {len(pdf_pages)} 页\n")

# 2. 定义文本清理函数（去除特定换行和符号）
def clean_text(text):
    pattern = re.compile(r'[^\u4e00-\u9fff](\n)[^\u4e00-\u9fff]', re.DOTALL)
    text = re.sub(pattern, lambda match: match.group(0).replace('\n', ''), text)
    text = text.replace('•', '').replace(' ', '')
    return text

# 3. 遍历所有页，打印原始和清理后的内容
for i, page in enumerate(pdf_pages):
    print(f"第 {i+1} 页的描述性数据：{page.metadata}")
    print(f"第 {i+1} 页的原始内容:\n{page.page_content}\n")
    
    cleaned_content = clean_text(page.page_content)
    print(f"第 {i+1} 页的清理后内容:\n{cleaned_content}")
    print("=" * 80)
