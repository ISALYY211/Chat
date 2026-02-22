import socket
import threading
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12345


def receive(sock: socket.socket):
    """Listen for incoming messages and print them."""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\nDisconnected from server.")
                break
            sys.stdout.write(data.decode())
            sys.stdout.flush()
        except OSError:
            break


def main():
    host = input(f"Server IP [{DEFAULT_HOST}]: ").strip() or DEFAULT_HOST
    port_str = input(f"Port [{DEFAULT_PORT}]: ").strip()
    port = int(port_str) if port_str else DEFAULT_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Could not connect to {host}:{port}. Is the server running?")
        return

    receiver = threading.Thread(target=receive, args=(sock,), daemon=True)
    receiver.start()

    try:
        while True:
            message = input()
            if message.lower() == "/quit":
                break
            sock.sendall((message + "\n").encode())
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("Goodbye!")
        sock.close()


if __name__ == "__main__":
    main()
