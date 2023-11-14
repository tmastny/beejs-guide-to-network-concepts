import sys
import socket
import json
import threading

from chatui import init_windows, read_command, print_message, end_windows
from server import get_next_packet

RECV_SIZE = 4


def send_packet(packet, s):
    packet = json.dumps(packet).encode()

    nbytes = len(packet).to_bytes(2)

    s.sendall(nbytes + packet)


def send_message(message, s):
    send_packet({"type": "chat", "message": message}, s)


def send_hello(nick, s):
    send_packet({"type": "hello", "nick": nick}, s)


def command(message):
    cmd = message[1:]
    if cmd == "q":
        return "quit"
    else:
        print_message(f"command {cmd} not supported.")

def print_packet(packet):
    packet = json.loads(packet)

    if packet["type"] == "chat":
        print_message(f'{packet["nick"]}: {packet["message"]}')
    elif packet["type"] == "join":
        print_message(f'*** {packet["nick"]} has joined the chat')
    elif packet["type"] == "leave":
        print_message(f'*** {packet["nick"]} has left the chat')



def receive_message(s: socket.socket):
    buffers = {s: b""}
    
    while True:
        packet = get_next_packet(s, buffers)
        print_packet(packet)


def setup_ui(s):
    init_windows()
    t1 = threading.Thread(target=receive_message, daemon=True, args=(s,))
    t1.start()


def main(argv):
    nick = argv[1]
    address = argv[2]
    port = int(argv[3])

    s = socket.socket()
    s.connect((address, port))
    send_hello(nick, s)

    setup_ui(s)

    while True:
        try:
            message = read_command(f"{nick}> ")
        except:
            break

        if message.startswith("/"):
            action = command(message)
            if action == "quit":
                break
        else:
            send_message(message, s)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
