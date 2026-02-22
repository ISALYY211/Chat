import asyncio
import json
import pathlib
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import websockets

HOST = "0.0.0.0"
HTTP_PORT = 8000
WS_PORT = 8765

HTML_PATH = pathlib.Path(__file__).with_name("index.html")

clients: dict[websockets.WebSocketServerProtocol, str] = {}


class HTTPHandler(BaseHTTPRequestHandler):
    def address_string(self):
        return self.client_address[0]

    def do_GET(self):
        html = HTML_PATH.read_text(encoding="utf-8")
        html = html.replace("{{WS_PORT}}", str(WS_PORT))
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def run_http():
    HTTPServer((HOST, HTTP_PORT), HTTPHandler).serve_forever()


async def broadcast(msg: dict, sender=None):
    payload = json.dumps(msg)
    for ws in list(clients):
        if ws is not sender:
            try:
                await ws.send(payload)
            except websockets.ConnectionClosed:
                pass


async def handler(websocket):
    nick = None
    try:
        async for raw in websocket:
            msg = json.loads(raw)

            if msg["type"] == "join":
                nick = msg["nickname"]
                clients[websocket] = nick
                print(f"[+] {nick} joined")
                await broadcast(
                    {"type": "system", "text": f"{nick} joined the chat"}
                )

            elif msg["type"] == "message" and nick:
                text = msg["text"]
                print(f"{nick}: {text}")
                await broadcast(
                    {"type": "chat", "nickname": nick, "text": text},
                    sender=websocket,
                )

            elif msg["type"] == "typing" and nick:
                await broadcast(
                    {"type": "typing", "nickname": nick},
                    sender=websocket,
                )
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.pop(websocket, None)
        if nick:
            print(f"[-] {nick} left")
            await broadcast({"type": "system", "text": f"{nick} left the chat"})


async def main():
    threading.Thread(target=run_http, daemon=True).start()

    async with websockets.serve(handler, HOST, WS_PORT):
        print(f"Chat server running!")
        print(f"  Web UI:     http://localhost:{HTTP_PORT}")
        print(f"  WebSocket:  ws://localhost:{WS_PORT}")
        print(f"  (Press Ctrl+C to stop)")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
