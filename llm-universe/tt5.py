import os
import time
import hmac
import base64
import hashlib
import json
import ssl
import websocket
from urllib.parse import urlencode
from dotenv import load_dotenv
import threading

load_dotenv()

# 获取接口
APPID = os.getenv("IFLYTEK_SPARK_APP_ID")
API_KEY = os.getenv("IFLYTEK_SPARK_API_KEY")
API_SECRET = os.getenv("IFLYTEK_SPARK_API_SECRET")
#WebSocket连接的主机名和路径
host = "spark-api.xf-yun.com"
path = "/v4.0/chat"
url = f"wss://{host}{path}"
# 字符转化
def create_url():
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(API_SECRET.encode(), signature_origin.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode()).decode()
    query_params = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    return f"{url}?{urlencode(query_params)}"

# 储存历史回答上下文
full_answer = []
def on_message(ws, message):
    global full_answer
    try:
        data = json.loads(message)
        if "payload" in data and "choices" in data["payload"]:
            choices = data["payload"]["choices"]
            text_list = choices.get("text", [])
            for item in text_list:
                content = item.get("content", "")
                full_answer.append(content)
                print(content, end="", flush=True)
            if choices.get("status") == 2:
                print("\n")  # 换行，完成本轮回答
                full_answer = []  # 清空缓存，为下一轮做准备
                print(" 请输入你的下一句话 (输入exit退出)：")
        else:
            print("\n响应中无有效payload字段，可能请求失败，返回内容：", data)
    except Exception as e:
        print("\n解析错误:", e)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("\nWebSocket closed")

def on_open(ws):
    print("WebSocket 已连接，开始对话...")
    print("你好，我是星火AI：")
    def run():
        while True:
            user_input = input()
            if user_input.strip().lower() == "exit":
                print("退出程序")
                ws.close()
                break
            if not user_input.strip():
                print("请输入有效内容")
                continue
            payload = {
                "header": {
                    "app_id": APPID,
                    "uid": "user_001"
                },
                "parameter": {
                    "chat": {
                        "domain": "4.0Ultra",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                },
                "payload": {
                    "message": {
                        "text": [
                            {"role": "user", "content": user_input}
                        ]
                    }
                }
            }
            ws.send(json.dumps(payload))
    threading.Thread(target=run, daemon=True).start()
# 主程序，启动连接
if __name__ == "__main__":
    ws_url = create_url()
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
