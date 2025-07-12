from openai import OpenAI

API_KEY = "sk-6OMLotNhr9SoeBS0AhNFcf3o1XBWOeLuV7Sx6SDjbyLX4klx"

# 创建 OpenAI 客户端
client = OpenAI(
    api_key="sk-6OMLotNhr9SoeBS0AhNFcf3o1XBWOeLuV7Sx6SDjbyLX4klx", 
    base_url="https://api.kimi.com",
)

def chat_with_kimi():
    print("欢迎使用 KIMI！输入 'exit' 退出。")
    conversation_history = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手。你更擅长中文和英文的对话。你会为用户提供安全、有帮助、准确的回答。同时，你会拒绝一切涉及恐怖主义、种族歧视、黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"
        }
    ]

    while True:
        user_input = input("\n用户：")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("再见！")
            break

        # 将用户输入添加到对话历史中
        conversation_history.append({"role": "user", "content": user_input})

        # 构造请求数据
        data = {
            "model": "moonshot-v1-8k",  # 替换为实际支持的模型名称
            "messages": conversation_history,
            "temperature": 0.3
        }

        try:
            # 发送请求到 Kimi API
            response = client.chat.completions.create(**data)
            assistant_message = response.choices[0].message.content
            print(f"Kimi: {assistant_message}")

            # 将 Kimi 回复添加到对话历史中
            conversation_history.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            print(f"请求失败: {e}")

# 启动聊天
if __name__ == "__main__":
    chat_with_kimi()