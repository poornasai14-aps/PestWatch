"""Entry point: python run.py  ->  http://127.0.0.1:8000 (and your LAN IP).

Binds 0.0.0.0 so you can open it on your phone over the same Wi-Fi
(http://<your-PC-IP>:8000). Note: installing the PWA on a phone needs HTTPS,
so for phone install use a tunnel like ngrok; on this PC's Chrome/Edge,
http://localhost:8000 is a secure context and installs directly.
"""
import socket
import uvicorn


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    print(f"\n  PestWatch -> http://localhost:8000   (this PC)")
    print(f"            -> http://{lan_ip()}:8000   (phone on same Wi-Fi)\n")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
