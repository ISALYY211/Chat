# Chat

A simple chat app built with Python — for educational purposes.

## Web version (recommended)

Uses WebSockets and a browser-based UI.

1. Start the server:

   ```
   uv run web_server.py
   ```

2. Open `http://localhost:8000` in a browser (or `http://YOUR_LAN_IP:8000` from other devices).

3. Pick a nickname and start chatting.

Features: chat messages, join/leave notifications, and timing-based typing indicators.

## Terminal version

Uses raw TCP sockets and a terminal-based client.

- **`server.py`** — TCP server on port 12345
- **`client.py`** — terminal client with typing indicators (Windows + macOS/Linux)

```
uv run server.py          # terminal 1
uv run client.py          # terminal 2+
```
