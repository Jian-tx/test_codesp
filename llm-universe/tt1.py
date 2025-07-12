# coding: utf-8
import json
import base64
import hashlib
import hmac
import os
import threading
import ssl
from urllib.parse import urlparse, urlencode
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import websocket
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('apikey.env')

class Ws_Param:
    """WebSocket参数生成类"""
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        """生成鉴权URL"""
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(
            self.APISecret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        return self.Spark_url + '?' + urlencode(v)

class SparkAPI:
    def __init__(self):
        self.content = []
        self.completion_flag = threading.Event()
        self.error_occurred = False

    def on_error(self, ws, error, *args):
        """优化错误处理回调"""
        self.error_occurred = True
        print(f"\n❌ 发生错误: {str(error)}")
        self.completion_flag.set()

    def on_close(self, ws, close_status_code=None, close_msg=None, *args):
        """优化关闭回调"""
        if not self.error_occurred:
            if close_status_code == 1000:
                print("\n✅ 会话正常结束")
            else:
                print(f"\n⚠️ 连接关闭 - 状态码: {close_status_code}, 消息: {close_msg}")
        self.completion_flag.set()

    def on_open(self, ws, *args):
        """优化连接成功回调"""
        print("🔗 连接建立成功，发送请求...")
        def run():
            try:
                data = json.dumps(self.gen_params(
                    appid=ws.appid,
                    query=ws.query,
                    domain=ws.domain,
                    temperature=ws.temperature
                ))
                ws.send(data)
            except Exception as e:
                print(f"\n❌ 请求发送失败: {str(e)}")
                self.completion_flag.set()
        threading.Thread(target=run).start()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data['header']['code'] != 0:
                print(f"\n❌ API错误: {data['header']['message']}")
                return

            # 提取内容并实时拼接
            content = data["payload"]["choices"]["text"][0]["content"]
            print(content, end='', flush=True)
            self.content.append(content)  # 确保内容被收集

            # 检测是否结束
            if data["payload"]["choices"]["status"] == 2:
                self.completion_flag.set()
        except Exception as e:
            print(f"\n❌ 消息处理失败: {str(e)}")
            self.completion_flag.set()

    def gen_params(self, appid, query, domain, temperature):
        """生成请求参数"""
        return {
            "header": {"app_id": appid, "uid": "1234"},
            "parameter": {"chat": {
                "domain": domain,
                "temperature": temperature,
                "max_tokens": 4096,
                "auditing": "default"
            }},
            "payload": {"message": {"text": [{"role": "user", "content": query}]}}
        }

    def get_completion(self, prompt, model="Spark Max", temperature=0.5):
        """获取大模型响应（带友好提示）"""
        print(f"\n🔄 正在连接【{model}】模型，请稍候...")
        try:
            # 获取环境变量
            appid = os.getenv("APPID")
            api_key = os.getenv("APIKey")
            api_secret = os.getenv("APISecret")
            
            if not all([appid, api_key, api_secret]):
                raise ValueError("❌ 环境变量验证失败，请检查apikey.env文件")

            # 配置模型参数
            model_config = {
                "Spark Max": {
                    "url": "wss://spark-api.xf-yun.com/v3.5/chat",
                    "domain": "generalv3.5"
                },
                "Spark 4.0 Ultra": {
                    "url": "wss://spark-api.xf-yun.com/v4.0/chat",
                    "domain": "generalv4"
                },
                "Spark Pro": {
                    "url": "wss://spark-api.xf-yun.com/v3.1/chat",
                    "domain": "generalv3"
                }
            }.get(model)
            
            if not model_config:
                raise ValueError(f"❌ 不支持的模型: {model}")

            # 重置状态
            self.content = []
            self.completion_flag.clear()
            self.error_occurred = False

            # 创建WebSocket连接
            ws_param = Ws_Param(
                APPID=appid,
                APIKey=api_key,
                APISecret=api_secret,
                Spark_url=model_config["url"]
            )
            ws_url = ws_param.create_url()

            websocket.enableTrace(False)
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 附加参数
            ws.appid = appid
            ws.query = prompt
            ws.domain = model_config["domain"]
            ws.temperature = temperature
            
            # 启动连接（设置超时60秒）
            ws.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_timeout=60
            )
            
            # 等待完成
            self.completion_flag.wait(timeout=60)
            return "".join(self.content) if not self.error_occurred else None
            
        except Exception as e:
            print(f"\n❌ 系统错误: {str(e)}")
            return None

if __name__ == "__main__":
    spark = SparkAPI()
    
    # 测试1：正常请求
    print("="*50)
    print("测试正常请求：")
    response = spark.get_completion(
        prompt="给我写一篇100字的晨景描写",
        model="Spark Max",
        temperature=0.5
    )
    print("\n\n💡 完整响应：")
    print(response if response else "（无有效响应）")
