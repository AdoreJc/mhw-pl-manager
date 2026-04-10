"""python -m mhw_pl_manager — 启动本地 Web 服务。"""
import threading
import time
import webbrowser

import uvicorn

_HOST = "127.0.0.1"
_PORT = 8765


def _open_browser_after_ready() -> None:
    time.sleep(0.7)
    webbrowser.open(f"http://{_HOST}:{_PORT}/")


if __name__ == "__main__":
    threading.Thread(target=_open_browser_after_ready, daemon=True).start()
    uvicorn.run(
        "mhw_pl_manager.main:app",
        host=_HOST,
        port=_PORT,
        reload=False,
    )
