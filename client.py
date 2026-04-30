import socket
import time

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8080

SERVER_HOST = '127.0.0.1'
UDP_PORT = 9000


# =========================
# HTTP CLIENT
# =========================
def http_request():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((PROXY_HOST, PROXY_PORT))

    request = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    client_socket.sendall(request.encode())

    response = b""
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data

    print("\n=== HTTP RESPONSE ===\n")
    print(response.decode(errors='ignore'))

    client_socket.close()


# =========================
# UDP QoS TEST
# =========================
def udp_test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    rtts = []
    lost = 0

    for i in range(10):
        send_time = time.time()
        message = f"Ping {i} {send_time}".encode()

        try:
            sock.sendto(message, (SERVER_HOST, UDP_PORT))
            data, _ = sock.recvfrom(1024)

            rtt = (time.time() - send_time) * 1000
            rtts.append(rtt)

            print(f"Ping {i}: {rtt:.2f} ms")

        except socket.timeout:
            print(f"Ping {i}: Request timed out")
            lost += 1

    if rtts:
        print("\n=== QoS RESULT ===")
        print(f"Min RTT: {min(rtts):.2f} ms")
        print(f"Avg RTT: {sum(rtts)/len(rtts):.2f} ms")
        print(f"Max RTT: {max(rtts):.2f} ms")

        jitter = [abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))]
        if jitter:
            print(f"Jitter: {sum(jitter)/len(jitter):.2f} ms")

    print(f"Packet Loss: {lost*10}%\n")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    http_request()
    udp_test()
