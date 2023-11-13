import sys
import socket
import json


def handle_response(s):
    print(s.recv(1024))


def send_packet(packet, s):
    packet = json.dumps(packet).encode()

    nbytes = len(packet).to_bytes(2)

    s.sendall(nbytes + packet)


def main(argv):
    nick = argv[1]
    address = argv[2]
    port = int(argv[3])

    s = socket.socket()
    s.connect((address, port))

    hello = {"type": "hello", "nick": nick}
    send_packet(hello, s)
    handle_response(s)

    message = {"type": "chat", "message": f"Hi everyone, I'm {nick}"}
    send_packet(message, s)
    handle_response(s)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
