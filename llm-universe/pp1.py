import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_ = load_dotenv(find_dotenv())
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    temperature=0.0,
    openai_api_key=openai_api_key,
    base_url="https://xiaoai.plus/v1"
)

response = llm.invoke("请你自我介绍一下自己！")
print(response.content)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译助手，可以帮助我将 {input_language} 翻译成 {output_language}。"),
    ("human", "{text}")
])

output_parser = StrOutputParser()

#  创建链（Prompt → LLM → 输出解析）
chain = chat_prompt | llm | output_parser


text_zh = """我带着比身体重的行李，
游入尼罗河底，
经过几道闪电 看到一堆光圈，
不确定是不是这里。
"""
translation_en = chain.invoke({
    "input_language": "中文",
    "output_language": "英文",
    "text": text_zh
})
print(translation_en)

text_en = """I carried luggage heavier than my body and dived into the bottom of the Nile River.
After passing through several flashes of lightning, I saw a pile of halos, not sure if this is the place."""
print("\n>>> 英文 → 中文：")
translation_zh = chain.invoke({
    "input_language": "英文",
    "output_language": "中文",
    "text": text_en
})
print(translation_zh)
