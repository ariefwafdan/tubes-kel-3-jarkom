import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
TCP_PORT = 8000
UDP_PORT = 9000


# =========================
# UDP SERVER (QoS ECHO)
# =========================
def udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    print(f"[UDP] running on {UDP_PORT}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        udp_socket.sendto(data, addr)


threading.Thread(target=udp_server, daemon=True).start()


# =========================
# HANDLE CLIENT (THREAD)
# =========================
def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode(errors='ignore')

        request_line = request.split('\n')[0]
        method, path, version = request_line.split()

        if path == "/":
            path = "/index.html"

        file_path = path[1:]

        with open(file_path, 'rb') as f:
            content = f.read()

        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(content)}\r\n"
            "\r\n"
        )

        response = header.encode() + content
        status = "200 OK"

    except FileNotFoundError:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Not Found</h1>"
        status = "404 Not Found"
        file_path = "UNKNOWN"

    except Exception as e:
        response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>500 Error</h1>"
        status = "500 Error"
        file_path = "UNKNOWN"
        print("[ERROR]", e)

    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {client_address[0]} - {file_path} - {status}")

    client_socket.sendall(response)
    client_socket.close()


# =========================
# TCP SERVER
# =========================
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, TCP_PORT))
tcp_socket.listen(5)

print(f"[HTTP] running on {TCP_PORT}")

while True:
    client_socket, client_address = tcp_socket.accept()

    threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    ).start()
