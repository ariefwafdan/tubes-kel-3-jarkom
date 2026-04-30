import socket
import threading
import os
from datetime import datetime

PROXY_HOST = '0.0.0.0'
PROXY_PORT = 8080

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(4096)

        request_str = request.decode(errors='ignore')
        request_line = request_str.split('\n')[0]
        method, path, version = request_line.split()

        if path == "/":
            path = "/index.html"

        cache_path = os.path.join(CACHE_DIR, path[1:])

        # =================
        # CACHE HIT
        # =================
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                response = f.read()

            status = "HIT"
            client_socket.sendall(response)

        else:
            # =================
            # CACHE MISS
            # =================
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(3)

            server_socket.connect((SERVER_HOST, SERVER_PORT))
            server_socket.sendall(request)

            response = b""
            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                response += data

            server_socket.close()

            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            with open(cache_path, 'wb') as f:
                f.write(response)

            status = "MISS"
            client_socket.sendall(response)

    except socket.timeout:
        response = b"HTTP/1.1 504 Gateway Timeout\r\n\r\n<h1>504 Gateway Timeout</h1>"
        client_socket.sendall(response)
        status = "504"

    except Exception as e:
        print("[ERROR]", e)
        response = b"HTTP/1.1 502 Bad Gateway\r\n\r\n<h1>502 Bad Gateway</h1>"
        client_socket.sendall(response)
        status = "502"

    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {client_address[0]} - {path} - {status}")

    client_socket.close()


proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind((PROXY_HOST, PROXY_PORT))
proxy_socket.listen(5)

print(f"[PROXY] running on {PROXY_PORT}")

while True:
    client_socket, client_address = proxy_socket.accept()

    threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    ).start()
