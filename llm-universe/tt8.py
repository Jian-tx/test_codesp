import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 加载本地 .env 文件中的环境变量
_ = load_dotenv(find_dotenv())

def openai_embedding(text: str, model: str = None):
    # 获取 API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未能读取 OPENAI_API_KEY，请检查 .env 文件或环境变量设置。")

    # 使用小爱接口替代官方的 OpenAI 地址
    client = OpenAI(
        api_key=api_key,
        base_url="https://xiaoai.plus/v1"  
    )

    if model is None:
        model = "text-embedding-3-small"

    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response

response = openai_embedding(text='要生成 embedding 的输入文本，字符串形式。')

print(f'返回的embedding类型为：{response.object}')
print(f'embedding长度为：{len(response.data[0].embedding)}')
print(f'embedding（前10）为：{response.data[0].embedding[:10]}')
print(f'本次embedding model为：{response.model}')
print(f'本次token使用情况为：{response.usage}')

