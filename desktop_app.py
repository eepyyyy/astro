import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import time
import socket
import threading
import subprocess
import urllib.request
import uvicorn
import uvicorn.logging
import uvicorn.loops
import uvicorn.loops.auto
import uvicorn.loops.asyncio
import uvicorn.protocols
import uvicorn.protocols.http
import uvicorn.protocols.http.auto
import uvicorn.protocols.http.h11_impl
import uvicorn.protocols.websockets
import uvicorn.protocols.websockets.auto
import uvicorn.lifespan
import uvicorn.lifespan.on
import uvicorn.lifespan.off
import anyio
import anyio._backends
import anyio._backends._asyncio

import server
from server import app


def is_jamakkol_server_running(port: int = 8080, timeout: float = 0.6) -> bool:
    try:
        proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/vault/info",
            headers={"Cache-Control": "no-cache"},
        )
        with opener.open(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def is_port_free(port: int) -> bool:
    """Instant (0.05ms) check whether a local TCP port can be bound."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def find_available_port(preferred_port: int = 8080) -> int:
    if is_port_free(preferred_port):
        return preferred_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def find_electron_runtime() -> tuple[str | None, str | None]:
    """
    Locate the native Electron binary (electron.exe) and the Electron app directory
    containing package.json & electron/main.js from any launch location:
    - dist/JamakkolHoraStudio/JamakkolHoraStudio.exe
    - release/JamakkolHoraStudio_Portable.exe
    - Installed %LOCALAPPDATA%/Programs/JamakkolHoraStudio/JamakkolHoraStudio.exe
    - Project root d:/Gana/Jamakkol Prasanam
    """
    exe_dir = (
        os.path.dirname(os.path.abspath(sys.executable))
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    meipass_dir = getattr(sys, "_MEIPASS", exe_dir)
    one_up = os.path.abspath(os.path.join(exe_dir, ".."))
    two_up = os.path.abspath(os.path.join(exe_dir, "..", ".."))

    search_roots = [
        exe_dir,
        meipass_dir,
        os.path.join(exe_dir, "_internal"),
        one_up,
        os.path.join(one_up, "dist", "JamakkolHoraStudio"),
        two_up,
        os.path.join(two_up, "dist", "JamakkolHoraStudio"),
        os.path.dirname(os.path.abspath(__file__)),
    ]

    for root in search_roots:
        if not root or not os.path.isdir(root):
            continue

        # 1. Check bundled electron_runtime folder
        e_bin_bundled = os.path.join(root, "electron_runtime", "electron.exe")
        app_dir_bundled = os.path.join(root, "electron_app")
        if os.path.isfile(e_bin_bundled) and os.path.isfile(os.path.join(app_dir_bundled, "package.json")):
            return e_bin_bundled, app_dir_bundled

        # 2. Check node_modules/electron/dist/electron.exe
        e_bin_node = os.path.join(root, "node_modules", "electron", "dist", "electron.exe")
        if os.path.isfile(e_bin_node) and os.path.isfile(os.path.join(root, "package.json")):
            return e_bin_node, root

    return None, None


def run_server(port: int):
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        log_config=None,
    )
    uv_server = uvicorn.Server(config)
    uv_server.run()


def main():
    if "--server-only" in sys.argv:
        idx = sys.argv.index("--server-only")
        port = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else find_available_port(8080)
        run_server(port)
        return

    # Instant check: if port 8080 is free, start server immediately without a 2s TCP timeout stall
    if is_port_free(8080):
        port = 8080
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()
    elif is_jamakkol_server_running(8080):
        port = 8080
    else:
        port = find_available_port(8081)
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()

    electron_bin, electron_app_dir = find_electron_runtime()
    if electron_bin and electron_app_dir:
        env = os.environ.copy()
        for k in list(env.keys()):
            if k.upper() == "ELECTRON_RUN_AS_NODE":
                env.pop(k, None)
        env["JAMAKKOL_BACKEND_PORT"] = str(port)
        proc = subprocess.Popen([electron_bin, electron_app_dir], cwd=electron_app_dir, env=env)
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
    else:
        while True:
            time.sleep(2.0)


if __name__ == "__main__":
    main()
