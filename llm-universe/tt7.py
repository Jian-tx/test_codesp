import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# 读取本地/项目的环境变量
_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY2"),
    base_url="https://api.deepseek.com/v1",
)

def main():
    print("DeepSeek AI 对话开启，输入 'exit' 或 'quit' 退出。\n")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    while True:
        user_input = input("用户：").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("对话结束，再见！")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            ai_reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": ai_reply})

            print("AI：" + ai_reply)

        except Exception as e:
            print("发生错误：", e)
            break

if __name__ == "__main__":
    main()

