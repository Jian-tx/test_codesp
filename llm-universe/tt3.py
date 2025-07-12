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

APPID = os.getenv("IFLYTEK_SPARK_APP_ID")
API_KEY = os.getenv("IFLYTEK_SPARK_API_KEY")
API_SECRET = os.getenv("IFLYTEK_SPARK_API_SECRET")

host = "spark-api.xf-yun.com"
path = "/v4.0/chat"
url = f"wss://{host}{path}"

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

# 全局对话上下文，保存历史消息
message_history = []

def on_message(ws, message):
    global message_history
    try:
        data = json.loads(message)
        if "payload" in data and "choices" in data["payload"]:
            choices = data["payload"]["choices"]
            text_list = choices.get("text", [])
            for item in text_list:
                content = item.get("content", "")
                print(content, end="", flush=True)
                # 追加助手回复到上下文
                message_history.append({"role": "assistant", "content": content})
            if choices.get("status") == 2:  # 2表示本轮回答结束
                print("\n➡️ 请输入你的下一句话 (输入exit退出)：")
        else:
            print("\n⚠️ 响应中无有效payload字段，返回：", data)
    except Exception as e:
        print("\n解析错误:", e)

def on_error(ws, error):
    print("❌ WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("\n🔒 WebSocket closed")

def on_open(ws):
    print("✅ WebSocket 已连接，开始对话...")
    print("➡️ 请输入你的问题 (输入exit退出)：")

    def run():
        global message_history
        while True:
            user_input = input()
            if user_input.strip().lower() == "exit":
                print("退出程序")
                ws.close()
                break
            if not user_input.strip():
                print("请输入有效内容")
                continue
            # 追加用户输入到上下文
            message_history.append({"role": "user", "content": user_input})

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
                        "text": message_history
                    }
                }
            }
            ws.send(json.dumps(payload))

    threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    ws_url = create_url()
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
