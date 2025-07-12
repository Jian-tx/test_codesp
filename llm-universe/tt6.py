import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# 加载 .env 文件中的环境变量
_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://xiaoai.plus/v1",
)

def main():
    print("Hello,how can I assist you today?")
    #记忆历史
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    while True:
        user_input = input("用户：").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("结束对话，再见！")
            break

        # 把用户输入添加到对话历史
        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            ai_message = response.choices[0].message.content

            # 把 AI 回复也加入对话历史，保证上下文连续
            messages.append({"role": "assistant", "content": ai_message})

            print("AI:" + ai_message)

        except Exception as e:
            print("调用失败:", e)
            break

if __name__ == "__main__":
    main()




