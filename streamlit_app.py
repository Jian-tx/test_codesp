import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_community.vectorstores import Chroma  # 只用Chroma
from chromadb.config import Settings

openai_api_key = st.secrets["OPENAI_API_KEY"]

from chromadb.config import Settings  # 新增

def get_retriever():
    embedding = OpenAIEmbeddings(
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        openai_api_base="https://xiaoai.plus/v1"
    )
    client_settings = Settings(
        chroma_api_impl="rest",
        chroma_server_host="localhost",  # 如果不是本机，改为服务器IP
        chroma_server_http_port="8000"
    )
    vectordb = Chroma(
        collection_name="your_collection",  # 替换为你的 collection 名称
        embedding_function=embedding,
        client_settings=client_settings
    )
    return vectordb.as_retriever()

def combine_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs["context"])

def get_qa_history_chain():
    retriever = get_retriever()
    llm = ChatOpenAI(
        temperature=0.0,
        openai_api_key=openai_api_key,
        base_url="https://xiaoai.plus/v1"   # 这里也加上 base_url
    )
    condense_question_system_template = (
        "请根据聊天记录总结用户最近的问题，"
        "如果没有多余的聊天记录则返回用户的问题。"
    )
    condense_question_prompt = ChatPromptTemplate([
        ("system", condense_question_system_template),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    retrieve_docs = RunnableBranch(
        (lambda x: not x.get("chat_history", False), (lambda x: x["input"]) | retriever, ),
        condense_question_prompt | llm | StrOutputParser() | retriever,
    )

    system_prompt = (
        "你是一个问答任务的助手。 "
        "请使用检索到的上下文片段回答这个问题。 "
        "如果你不知道答案就说不知道。 "
        "请使用简洁的话语回答用户。"
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )
    qa_chain = (
        RunnablePassthrough().assign(context=combine_docs)
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    qa_history_chain = RunnablePassthrough().assign(
        context=retrieve_docs,
    ).assign(answer=qa_chain)
    return qa_history_chain

def gen_response(chain, input, chat_history):
    response = chain.stream({
        "input": input,
        "chat_history": chat_history
    })
    for res in response:
        if "answer" in res.keys():
            yield res["answer"]

def main():
    st.markdown('### 🦜🔗 动手学大模型应用开发')
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "qa_history_chain" not in st.session_state:
        st.session_state.qa_history_chain = get_qa_history_chain()
    messages = st.container(height=550)
    for message in st.session_state.messages:
        with messages.chat_message(message[0]):
            st.write(message[1])
    if prompt := st.chat_input("Say something"):
        st.session_state.messages.append(("human", prompt))
        with messages.chat_message("human"):
            st.write(prompt)
        answer = gen_response(
            chain=st.session_state.qa_history_chain,
            input=prompt,
            chat_history=st.session_state.messages
        )
        with messages.chat_message("ai"):
            output = st.write_stream(answer)
        st.session_state.messages.append(("ai", output))

st.title("Hello Streamlit!")
st.write("如果你能看到这句话，说明 Streamlit 正常渲染了。")

if __name__ == "__main__":
    main()
