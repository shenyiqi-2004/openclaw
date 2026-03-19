"""
mouse_bridge.py - Windows TCP Socket Mouse Control Server

必须在当前登录用户的桌面 session 中运行，不能作为 service 或任务计划。
"""

import ctypes
import json
import socket
import sys
import threading
from ctypes import wintypes

HOST = "0.0.0.0"
PORT = 44555

# ==============================
# Win32 API Setup
# ==============================
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class _INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUTUNION),
    ]


# ==============================
# Win32 Function Bindings
# ==============================
user32.SetCursorPos.argtypes = [wintypes.INT, wintypes.INT]
user32.SetCursorPos.restype = wintypes.BOOL

user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.GetCursorPos.restype = wintypes.BOOL

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT


# ==============================
# Mouse Control Functions
# ==============================
def get_cursor_pos():
    """获取当前鼠标位置"""
    pt = wintypes.POINT()
    if not user32.GetCursorPos(ctypes.byref(pt)):
        err = ctypes.get_last_error()
        raise RuntimeError(f"GetCursorPos failed, error={err}")
    return {"x": pt.x, "y": pt.y}


def move_mouse(x: int, y: int):
    """移动鼠标到指定位置"""
    print(f"[Win32] SetCursorPos({x}, {y})")
    ok = user32.SetCursorPos(int(x), int(y))
    if not ok:
        err = ctypes.get_last_error()
        raise RuntimeError(f"SetCursorPos failed, error={err}")
    # 立即获取位置验证
    new_pos = get_cursor_pos()
    print(f"[Win32] SetCursorPos result: moved to {new_pos}")
    return new_pos


def left_click():
    """执行左键点击"""
    # 获取点击前位置
    pos_before = get_cursor_pos()
    print(f"[Win32] Left click at {pos_before}")

    inputs = (INPUT * 2)()

    # Mouse down
    inputs[0].type = INPUT_MOUSE
    inputs[0].mi = MOUSEINPUT(
        dx=0, dy=0, mouseData=0,
        dwFlags=MOUSEEVENTF_LEFTDOWN,
        time=0, dwExtraInfo=0
    )

    # Mouse up
    inputs[1].type = INPUT_MOUSE
    inputs[1].mi = MOUSEINPUT(
        dx=0, dy=0, mouseData=0,
        dwFlags=MOUSEEVENTF_LEFTUP,
        time=0, dwExtraInfo=0
    )

    sent = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    if sent != 2:
        err = ctypes.get_last_error()
        raise RuntimeError(f"SendInput failed, sent={sent}, error={err}")

    # 获取点击后位置
    pos_after = get_cursor_pos()
    print(f"[Win32] Left click done, now at {pos_after}")
    return pos_after


# ==============================
# Session Info
# ==============================
def get_session_info():
    """获取当前 session 信息"""
    hwnd_console = kernel32.GetConsoleWindow()
    hwnd_foreground = user32.GetForegroundWindow()
    return {
        "console_window": int(hwnd_console) if hwnd_console else 0,
        "foreground_window": int(hwnd_foreground) if hwnd_foreground else 0,
    }


# ==============================
# Command Handler
# ==============================
def handle_command(req: dict) -> dict:
    """处理客户端命令"""
    cmd = req.get("cmd")

    if cmd == "ping":
        return {
            "ok": True,
            "message": "pong",
            "session": get_session_info(),
            "cursor": get_cursor_pos(),
        }

    if cmd == "move":
        x = req.get("x")
        y = req.get("y")
        if x is None or y is None:
            return {"ok": False, "error": "move requires x and y"}
        try:
            pos = move_mouse(int(x), int(y))
            return {"ok": True, "cmd": "move", "cursor": pos}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "click":
        try:
            pos = left_click()
            return {"ok": True, "cmd": "click", "cursor": pos}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    return {"ok": False, "error": f"unknown cmd: {cmd}"}


# ==============================
# Client Handler
# ==============================
def client_thread(conn: socket.socket, addr):
    """处理客户端连接"""
    print(f"[Server] Client connected: {addr}")
    try:
        conn.settimeout(30.0)
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                line = data.decode("utf-8").strip()
                if not line:
                    continue

                print(f"[Server] Received: {line}")

                try:
                    req = json.loads(line)
                except json.JSONDecodeError as e:
                    resp = {"ok": False, "error": f"JSON parse error: {e}"}
                else:
                    resp = handle_command(req)

                resp_json = json.dumps(resp, ensure_ascii=False)
                print(f"[Server] Response: {resp_json}")
                conn.sendall((resp_json + "\n").encode("utf-8"))

            except socket.timeout:
                break
    except Exception as e:
        print(f"[Server] Client error: {e}")
    finally:
        print(f"[Server] Client disconnected: {addr}")
        conn.close()


# ==============================
# Main
# ==============================
def main():
    print("=" * 50)
    print("mouse_bridge.py - TCP Mouse Control Server")
    print("=" * 50)
    print(f"[Server] Listening on {HOST}:{PORT}")
    print(f"[Server] Session info: {get_session_info()}")
    print("[Server] Press Ctrl+C to stop")
    print("[Server] IMPORTANT: Run in logged-in desktop session!")
    print("=" * 50)

    # 立即测试一次 GetCursorPos 验证 Win32 可用
    try:
        pos = get_cursor_pos()
        print(f"[Server] Initial cursor position: {pos}")
    except Exception as e:
        print(f"[Server] WARNING: Cannot get cursor position: {e}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[Server] Ready, waiting for connections...")

        while True:
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
                t.start()
            except KeyboardInterrupt:
                print("\n[Server] Shutting down...")
                break


if __name__ == "__main__":
    main()
