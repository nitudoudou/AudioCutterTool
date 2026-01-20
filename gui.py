
import sys
import threading
import webview
from time import sleep
from app import app

# 全局变量控制服务状态
server_url = "http://127.0.0.1:54321"

def start_server():
    """在后台线程启动 Flask 服务"""
    try:
        app.run(host='127.0.0.1', port=54321, threaded=True)
    except Exception as e:
        print(f"Server error: {e}")

def on_closed():
    """窗口关闭时退出程序"""
    sys.exit(0)

if __name__ == '__main__':
    # 1. 启动 Flask 后台线程
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # 2. 等待一小会儿确保 Flask 启动
    sleep(0.5)

    # 3. 创建原生窗口
    window = webview.create_window(
        title='音频切割工具 v1.0',
        url=server_url,
        width=900,
        height=850,
        resizable=True,
        min_size=(800, 600)
    )

    # 4. 启动 GUI 循环
    # gui='edgechromium' 使用 Windows 内置的高性能 Edge WebView2 引擎
    webview.start(on_closed, gui='edgechromium', debug=False)
