import socket
import sys
import threading
import time

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12345

SIGNAL_PREFIX = "\x01"


def receive(sock: socket.socket):
    """Listen for incoming messages, handling typing signals separately."""
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\nDisconnected from server.")
                break
            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if line.startswith(SIGNAL_PREFIX):
                    signal = line[len(SIGNAL_PREFIX):]
                    if signal.startswith("TYPING:"):
                        name = signal[7:]
                        sys.stdout.write(f"\r  [{name} is typing...]   \n")
                        sys.stdout.flush()
                    elif signal.startswith("STOPPED:"):
                        name = signal[8:]
                        sys.stdout.write(f"\r  [{name} stopped typing]\n")
                        sys.stdout.flush()
                else:
                    sys.stdout.write(line + "\n")
                    sys.stdout.flush()
        except OSError:
            break


def send_signal(sock: socket.socket, signal: str):
    """Send a short control signal to the server."""
    try:
        sock.sendall(f"{SIGNAL_PREFIX}{signal}\n".encode())
    except OSError:
        pass


def input_loop_windows(sock: socket.socket):
    """Character-by-character input loop (Windows) with typing signals."""
    buffer = ""
    is_typing = False

    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwch()

            if char in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                if buffer:
                    if buffer.lower() == "/quit":
                        return
                    sock.sendall((buffer + "\n").encode())
                    buffer = ""
                if is_typing:
                    send_signal(sock, "STOPPED")
                    is_typing = False

            elif char == "\x08":  # Backspace
                if buffer:
                    buffer = buffer[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                if not buffer and is_typing:
                    send_signal(sock, "STOPPED")
                    is_typing = False

            elif char == "\x03":  # Ctrl+C
                raise KeyboardInterrupt

            else:
                if not is_typing:
                    send_signal(sock, "TYPING")
                    is_typing = True
                buffer += char
                sys.stdout.write(char)
                sys.stdout.flush()
        else:
            time.sleep(0.01)


def input_loop_fallback(sock: socket.socket):
    """Line-based input fallback (no typing indicators on non-Windows)."""
    while True:
        message = input()
        if message.lower() == "/quit":
            break
        sock.sendall((message + "\n").encode())


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

    welcome = sock.recv(1024).decode()
    sys.stdout.write(welcome)
    sys.stdout.flush()

    nickname = input()
    sock.sendall((nickname + "\n").encode())

    receiver = threading.Thread(target=receive, args=(sock,), daemon=True)
    receiver.start()

    try:
        if HAS_MSVCRT:
            input_loop_windows(sock)
        else:
            input_loop_fallback(sock)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("Goodbye!")
        sock.close()


if __name__ == "__main__":
    main()
