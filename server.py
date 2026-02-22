import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

clients: list[socket.socket] = []
lock = threading.Lock()


def broadcast(message: bytes, sender: socket.socket | None = None):
    """Send a message to every connected client except the sender."""
    with lock:
        for client in clients:
            if client is not sender:
                try:
                    client.sendall(message)
                except OSError:
                    pass


def handle_client(client: socket.socket, address: tuple[str, int]):
    """Handle a single client connection."""
    print(f"[+] {address} connected")
    client.sendall(b"Welcome! Type your nickname: ")

    try:
        nickname = client.recv(1024).decode().strip()
    except OSError:
        client.close()
        return

    if not nickname:
        nickname = f"{address[0]}:{address[1]}"

    broadcast(f"** {nickname} joined the chat **\n".encode(), sender=client)

    try:
        while True:
            data = client.recv(4096)
            if not data:
                break
            message = f"{nickname}: {data.decode()}"
            print(message, end="")
            broadcast(message.encode(), sender=client)
    except (OSError, ConnectionResetError):
        pass
    finally:
        with lock:
            clients.remove(client)
        broadcast(f"** {nickname} left the chat **\n".encode())
        client.close()
        print(f"[-] {address} disconnected")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client, address = server.accept()
            with lock:
                clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client, address), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
