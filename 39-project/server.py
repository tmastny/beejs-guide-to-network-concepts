import sys
import socket
import select
import json

RECV_SIZE = 5


class Clients:
    def __init__(self, listener=None):
        self.listener = listener
        self.sockets = {}
        self.add(listener)

        self.nicks: dict = {}

    @classmethod
    def SingleClient(cls, socket):
        client = cls()
        client.add(socket)

        return client

    def add(self, socket):
        self.sockets[socket] = {"buffer": b""}

    def set(self, socket, nick):
        self.sockets[socket]["nick"] = nick

        self.nicks[nick] = socket

    def getnick(self, socket):
        return self.sockets[socket]["nick"]

    def getsocket(self, nick):
        return self.nicks[nick]

    def remove(self, socket):
        nick = self.getnick(socket)
        self.sockets.pop(socket)

        self.nicks.pop(nick)

    def __getitem__(self, key):
        return self.sockets.__getitem__(key)

    def __iter__(self):
        skip_listener = lambda x: x != self.listener
        return filter(skip_listener, self.sockets.__iter__())

    def __contains__(self, key):
        return self.sockets.__contains__(key)


def send_response(response, clients):
    response = json.dumps(response).encode()

    nbytes = len(response).to_bytes(2)

    response = nbytes + response
    print(f"Sending... {response}")

    for s in clients:
        s.sendall(response)


def build_response(packet, sender: socket.socket, clients: Clients):
    """
    -> (response, recipients)
    """
    if packet == None:
        return ({"type": "leave", "nick": clients.getnick(sender)}, clients)

    payload = json.loads(packet)

    if payload["type"] == "hello":
        clients.set(sender, payload["nick"])
        return ({"type": "join", "nick": payload["nick"]}, clients)

    elif payload["type"] == "chat":
        response = {
            "type": "chat",
            "nick": clients.getnick(sender),
            "message": payload["message"],
        }
        return (response, clients)

    elif payload["type"] == "pm":
        sender_nick = clients.getnick(sender)
        response = {
            "type": "pm",
            "from": sender_nick,
            "to": payload["to"],
            "message": payload["message"],
        }

        recipients = Clients.SingleClient(sender)

        to_nick = payload["to"]
        if to_nick in clients.nicks:
            to_soc = clients.getsocket(payload["to"])
            recipients.add(to_soc)
        else:
            response = {
                "type": "error",
                "message": f"user {to_nick} is not in this chatroom",
            }

        return (response, recipients)
    elif payload["type"] == "users":
        users = [nick for nick in clients.nicks]
        response = {"type": "users", "users": users}

        return (response, Clients.SingleClient(sender))
    elif payload["type"] == "emote":
        sender_nick = clients.getnick(sender)
        response = {"type": "emote", "nick": sender_nick, "message": payload["message"]}

        return (response, clients)
    else:
        raise ValueError(f'Payload {payload["type"]} not supported.')


def get_next_packet(s: socket.socket, client_info: dict):
    buffer = client_info["buffer"]
    while True:
        buffer += s.recv(RECV_SIZE)

        if len(buffer) == 0:
            return None
        elif len(buffer) >= 2:
            length = int.from_bytes(buffer[:2])

            if len(buffer) >= 2 + length:
                packet = buffer[2 : length + 2]
                buffer = buffer[2 + length :]
                client_info["buffer"] = buffer

                return packet


def run_server(port):
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listener.bind(("", port))
    listener.listen()

    clients = Clients(listener)

    while True:
        ready_soc, _, _ = select.select(clients.sockets, {}, {})

        for soc in ready_soc:
            if soc == listener:
                new_soc, _ = soc.accept()
                clients.add(new_soc)
                continue

            packet = get_next_packet(soc, clients[soc])
            response, recipients = build_response(packet, soc, clients)

            if packet == None:
                clients.remove(soc)

            send_response(response, recipients)


def main(argv):
    port = int(argv[1])
    run_server(port)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
