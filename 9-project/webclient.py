from os import read
import socket
import sys

address = sys.argv[1]

port = 80
method = "GET"
content_file = ""
for i, arg in enumerate(sys.argv):
    if "--port" == arg:
        port = int(sys.argv[i + 1])
    elif "--method" == arg:
        method = sys.argv[i + 1]
        content_file = sys.argv[i + 2]

s = socket.socket()
s.connect((address, port))

if method == "GET":
    req = ["GET / HTTP/1.1", f"Host: {address}", "Connection: close"]
elif method == "POST":
    with open(content_file, mode="rb") as f:
        content = f.read()

    req = [
        "POST / HTTP/1.1",
        f"Host: {address}",
        "Content-Type: text/plain",
        f"Content-Length: {len(content)}",
        "",
        content.decode(),
    ]
else:
    raise ValueError("MethodNotSupported")

req = "\r\n".join(req) + "\r\n\r\n"
req = req.encode()
print(req)


s.sendall(req)

output = b""
while True:
    d = s.recv(1024)
    if len(d) == 0:
        break
    output += d

s.close()

print(output.decode())
