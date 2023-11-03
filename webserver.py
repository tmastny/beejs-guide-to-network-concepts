import socket
import sys

port = 28333
if len(sys.argv) > 1:
    port = sys.argv[1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)




