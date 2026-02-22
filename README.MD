# Chat

A simple TCP chat app built with Python sockets — for educational purposes.

## How it works

- **`server.py`** listens on `127.0.0.1:12345` and relays messages between all connected clients.
- **`client.py`** connects to the server, asks for a nickname, then lets you send and receive messages.

## Usage

1. Start the server in one terminal:

   ```
   uv run server.py
   ```

2. In another terminal (or several), start a client:

   ```
   uv run client.py
   ```

3. Type a nickname when prompted, then start chatting. Type `/quit` to disconnect.
