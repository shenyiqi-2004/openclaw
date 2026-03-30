"""
mouse_client.py - WSL TCP Mouse Control Client

自动从 /etc/resolv.conf 获取 Windows 主机地址。
"""

import json
import socket
import sys
import os


def get_windows_host() -> str:
    """自动从 /etc/resolv.conf 获取 Windows 主机 IP"""
    # 如果环境变量已设置，直接使用，不打印探测日志
    if os.environ.get("MOUSE_BRIDGE_HOST"):
        return os.environ.get("MOUSE_BRIDGE_HOST")
    
    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("nameserver"):
                    ip = line.strip().split()[1]
                    print(f"[Client] Found Windows host from resolv.conf: {ip}")
                    return ip
    except Exception as e:
        print(f"[Client] Warning: Could not read resolv.conf: {e}")

    # 回退到常见 WSL2 网关
    print("[Client] Using fallback gateway: 172.18.160.1")
    return "172.18.160.1"


# 默认从环境变量读取 host，或自动检测
HOST = os.environ.get("MOUSE_BRIDGE_HOST", get_windows_host())
PORT = 44555
TIMEOUT = 5.0


class MouseClient:
    def __init__(self, host=HOST, port=PORT, timeout=TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _send(self, payload: dict) -> dict:
        data = (json.dumps(payload) + "\n").encode("utf-8")

        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                print(f"[Client] Connected to {self.host}:{self.port}")
                sock.sendall(data)

                buf = b""
                while not buf.endswith(b"\n"):
                    chunk = sock.recv(4096)
                    if not chunk:
                        raise RuntimeError("Connection closed by server")
                    buf += chunk

                if not buf:
                    raise RuntimeError("No response from server")

                resp = json.loads(buf.decode("utf-8").strip())
                print(f"[Client] Response: {json.dumps(resp, ensure_ascii=False)}")
                return resp

        except ConnectionRefusedError:
            raise RuntimeError(f"Connection refused. Is mouse_bridge.py running on Windows?")
        except socket.timeout:
            raise RuntimeError(f"Connection timeout. Is mouse_bridge.py running?")
        except Exception as e:
            raise RuntimeError(f"Connection error: {e}")

    def ping(self) -> dict:
        return self._send({"cmd": "ping"})

    def move(self, x: int, y: int) -> dict:
        return self._send({"cmd": "move", "x": int(x), "y": int(y)})

    def click(self) -> dict:
        return self._send({"cmd": "click"})


def main():
    # 如果没有参数，打印帮助
    if len(sys.argv) < 2:
        print(f"mouse_client.py - TCP Mouse Control Client")
        print(f"Target: {HOST}:{PORT}")
        print()
        print("Usage:")
        print("  python3 mouse_client.py ping")
        print("  python3 mouse_client.py move 500 300")
        print("  python3 mouse_client.py click")
        print()
        print("Or set custom host:")
        print("  MOUSE_BRIDGE_HOST=192.168.1.100 python3 mouse_client.py ping")
        sys.exit(1)

    client = MouseClient()
    cmd = sys.argv[1]

    try:
        if cmd == "ping":
            resp = client.ping()
            print(json.dumps(resp, ensure_ascii=False, indent=2))

        elif cmd == "move":
            if len(sys.argv) != 4:
                raise SystemExit("Usage: python3 mouse_client.py move <x> <y>")
            x, y = int(sys.argv[2]), int(sys.argv[3])
            resp = client.move(x, y)
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            if not resp.get("ok"):
                sys.exit(1)

        elif cmd == "click":
            resp = client.click()
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            if not resp.get("ok"):
                sys.exit(1)

        else:
            raise SystemExit(f"Unknown command: {cmd}")

    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
