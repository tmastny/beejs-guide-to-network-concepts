import socket
import sys


def recieve(s) -> bytes:
    req = b""

    # recieve headers
    while True:
        print("waiting to recv...")
        d = s.recv(1024)
        req += d
        if b"\r\n\r\n" in d:
            break

    # recieve body if given content-length
    reqlines = req.decode().split("\r\n")

    content_length = 0
    for line in reqlines:
        if line == "":
            # The next lines are part of the body.
            # We don't want to search them
            break
        elif "Content-Length" in line:
            content_length = int(line.removeprefix("Content-Length: "))
            break

    if content_length > 0:
        nrecvs = content_length // 1024
        for _ in range(nrecvs):
            d = s.recv(1024)
            req += d

    return req


port = 28333
if len(sys.argv) > 1:
    port = sys.argv[1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(("", port))
s.listen()

while True:
    print("waiting to accept..")
    new_socket, (client_ip, client_port) = s.accept()

    print(f"accepted! Connected to {client_ip}:{client_port}")

    req = recieve(new_socket)
    print(req)

    if req.startswith(b"GET"):
        resp = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            "Content-Length: 6",
            "Connection: close",
            "",
            "Hello!",
        ]
    elif req.startswith(b"POST"):
        body = req.decode().split("\r\n\r\n")[1]
        print(body)

        message = "Hello! Post recieved."
        resp = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(message)}",
            "Connection: close",
            "",
            message,
        ]
    else:
        resp = ["HTTP/1.1 405 Method Not Allowed"]

    resp = "\r\n".join(resp) + "\r\n\r\n"
    resp = resp.encode()

    new_socket.sendall(resp)
    new_socket.close()
