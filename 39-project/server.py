import sys
import socket
import select
import json
from collections import defaultdict

RECV_SIZE = 5


class ClientInfo:
    def __init__(self):
        self.nick_to_socket = {}
        self.rooms = defaultdict(set)
        self.rooms["general"] = set()

        self.socket_to_client = {}

    def add(self, client):
        self.socket_to_client[client.socket] = client

    def join(self, socket, room):
        self.rooms[room].add(socket)

    def leave(self, socket, room):
        if room in self.rooms and socket in self.rooms[room]:
            self.rooms[room].remove(socket)

    def sockets(self):
        return self.socket_to_client.keys()

    def remove(self, socket):
        client = self.socket_to_client[socket]
        self.leave(socket, client.room)
        del self.socket_to_client[socket]
        del self.nick_to_socket[client.nick]


client_info = ClientInfo()


class Client:
    def __init__(self, socket: socket.socket):
        self.nick = None
        self.socket = socket
        self.buffer = {"buffer": b""}
        self.room = None
        client_info.add(self)

    def set_nick(self, nick):
        self.nick = nick
        client_info.nick_to_socket[nick] = self.socket

    def join(self, room):
        client_info.leave(self.socket, self.room)
        self.room = room
        client_info.join(self.socket, room)


def send_response(response, clients):
    response = json.dumps(response).encode()

    nbytes = len(response).to_bytes(2)

    response = nbytes + response
    print(f"Sending... {response}")

    for s in clients:
        s.sendall(response)


def build_response(packet, sender: Client):
    """
    -> [(response, recipients), ...]
    """
    if packet == None:
        response = {"type": "leave", "nick": sender.nick, "room": sender.room}
        recipients = client_info.rooms[sender.room]
        client_info.remove(sender.socket)
        return [(response, recipients)]

    payload = json.loads(packet)

    if payload["type"] == "hello":
        sender.set_nick(payload["nick"])
        sender.join("general")
        return [
            (
                {"type": "join", "nick": payload["nick"], "room": sender.room},
                client_info.rooms["general"],
            )
        ]

    elif payload["type"] == "join":
        leave_response = {
            "type": "leave",
            "nick": sender.nick,
            "room": sender.room,
        }
        leave_recipients = client_info.rooms[sender.room]

        sender.join(payload["room"])
        join_response = {
            "type": "join",
            "nick": sender.nick,
            "room": payload["room"],
        }
        join_recipients = client_info.rooms[payload["room"]]
        return [(leave_response, leave_recipients), (join_response, join_recipients)]

    elif payload["type"] == "rooms":
        response = {"type": "rooms", "rooms": list(client_info.rooms.keys())}
        return [(response, {sender.socket})]

    elif payload["type"] == "chat":
        response = {
            "type": "chat",
            "nick": sender.nick,
            "message": payload["message"],
        }
        return [(response, client_info.rooms[sender.room])]

    elif payload["type"] == "pm":
        response = {
            "type": "pm",
            "from": sender.nick,
            "to": payload["to"],
            "message": payload["message"],
        }

        recipients = {sender.socket}

        to_nick = payload["to"]
        if to_nick in client_info.nick_to_socket:
            to_soc = client_info.nick_to_socket[to_nick]
            recipients.add(to_soc)
        else:
            response = {
                "type": "error",
                "message": f"user {to_nick} is not in this chatroom",
            }

        return [(response, recipients)]
    elif payload["type"] == "users":
        room_sockets = client_info.rooms[sender.room]
        room_clients = [client_info.socket_to_client[s] for s in room_sockets]

        room_nicks = [c.nick for c in room_clients]
        response = {"type": "users", "users": room_nicks}

        return [(response, {sender.socket})]
    elif payload["type"] == "emote":
        response = {"type": "emote", "nick": sender.nick, "message": payload["message"]}

        return [(response, client_info.rooms[sender.room])]
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

    client_info.add(Client(listener))

    while True:
        ready_soc, _, _ = select.select(client_info.sockets(), {}, {})

        for soc in ready_soc:
            if soc == listener:
                new_soc, _ = soc.accept()
                client_info.add(Client(new_soc))
                continue

            client = client_info.socket_to_client[soc]
            packet = get_next_packet(soc, client.buffer)
            response_packages = build_response(packet, client)

            for response, recipients in response_packages:
                send_response(response, recipients)


def main(argv):
    port = int(argv[1])
    run_server(port)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
