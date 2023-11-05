from collections import namedtuple
import socket
import sys
import os


def recieve_all_bytes(s) -> bytes:
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


def recieve(s):
    req = recieve_all_bytes(s)
    req_parts = req.decode().split("\r\n\r\n")

    firstline = req_parts[0].split("\r\n")[0]
    method, path, _ = firstline.split(" ")  # protocol

    headers = req_parts[0].split("\r\n")[1:]
    body = req_parts[1]

    Req = namedtuple("Req", ["method", "path", "headers", "body"])
    return Req(method, path, headers, body)


def handle_get(req):
    if req.path == "/":
        files = [file for file in os.listdir() if os.path.splitext(file)[1] != ".py"]
        htmlized_files = [
            f'<li><a href="http://localhost:{port}/{file}">{file}</a></li>'
            for file in files
        ]

        body = (
            "<!DOCTYPE html><html><head><title>Available Files</title></head>"
            + f'<body><h1>Available Files</h1><ul>{"".join(htmlized_files)}</ul></body>'
        )

        return [
            "HTTP/1.1 200 OK",
            "Content-type: text/html",
            f"Content-Length: {len(body)}",
            "Connection: close",
            "",
            body,
        ]

    _, file = os.path.split(req.path)
    _, ext = os.path.splitext(file)

    ext_to_content_type = {".txt": "text/plain", ".html": "text/html"}
    if ext not in ext_to_content_type:
        body = f"404 Not Found. Content-Type {ext} not supported."
        return [
            "HTTP/1.1 404 Not Found",
            "Content-Type: text/plain",
            f"Content-Length: {len(body)}",
            "",
            body,
        ]

    http_resp = "HTTP/1.1 200 OK"
    try:
        with open(file, mode="r") as f:
            body = f.read()
    except:
        http_resp = "HTTP/1.1 404 Not Found"
        body = "404 Not Found"

    return [
        http_resp,
        f"Content-type: {ext_to_content_type[ext]}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        body,
    ]


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

    if req.method == "GET":
        resp = handle_get(req)
    elif req.method == "POST":
        print(req.body)

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