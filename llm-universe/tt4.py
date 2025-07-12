import os
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
_ = load_dotenv(find_dotenv())

# 初始化客户端  
client = ZhipuAI(api_key=os.environ["ZHIPUAI_API_KEY"])

def gen_glm_params(messages):
    '''
    构造 GLM 模型请求参数 messages
    这里直接传入历史对话消息列表，支持多轮上下文
    '''
    return messages

def get_completion(messages, model="glm-4-plus", temperature=0.95):
    '''
    获取 GLM 模型调用结果
    messages: [{"role": "user"|"assistant", "content": "..."}]格式的对话消息列表
    '''
    params = gen_glm_params(messages)
    try:   # 设置参数
        response = client.chat.completions.create(
            model=model,
            messages=params,
            temperature=temperature
        )   #检查响应
        if len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "generate answer error"
    except Exception as e:
        return f"调用接口出错: {e}"

def main():  #对话逻辑函数
    print("欢迎使用智谱GLM对话，输入 exit 退出")
    conversation = []
    while True:
        user_input = input("用户: ").strip()
        if user_input.lower() == "exit":
            print("退出程序")
            break
        if not user_input:
            print("请输入有效内容")
            continue
        conversation.append({"role": "user", "content": user_input})
        answer = get_completion(conversation)
        print("智谱:", answer)
        conversation.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
