import sys
import socket
import select
import json

RECV_SIZE = 5


def send_response(response, sockets, listener):
    response = json.dumps(response).encode()

    nbytes = len(response).to_bytes(2)
    
    response = nbytes + response
    print(f"Sending... {response}")

    for s in sockets:
        if s == listener:
            continue

        s.sendall(response)


def parse_packet(packet, client_info: dict) -> dict:
    if packet == None:
        return {"type": "leave", "nick": client_info["nick"]}

    payload = json.loads(packet)

    if payload["type"] == "hello":
        client_info["nick"] = payload["nick"]

        return {"type": "join", "nick": client_info["nick"]}

    elif payload["type"] == "chat":
        return {
            "type": "chat",
            "nick": client_info["nick"],
            "message": payload["message"],
        }

    else:
        raise ValueError(f'Payload {payload["type"]} not supported.')


def get_next_packet(s: socket.socket, buffers: dict):
    buffer = buffers[s]
    while True:
        buffer += s.recv(RECV_SIZE)

        if len(buffer) == 0:
            return None
        elif len(buffer) >= 2:
            length = int.from_bytes(buffer[:2])

            if len(buffer) >= 2 + length:
                packet = buffer[2 : length + 2]
                buffer = buffer[2 + length :]
                buffers[s] = buffer

                return packet


def run_server(port):
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listener.bind(("", port))
    listener.listen()

    sockets = {listener}
    soc_buffers = {}
    client_info = {}

    while True:
        ready_to_read, _, _ = select.select(sockets, {}, {})

        for soc in ready_to_read:
            if soc == listener:
                new_soc, _ = soc.accept()
                sockets.add(new_soc)
                soc_buffers[new_soc] = b""

                client_info[new_soc] = {}
                continue

            packet = get_next_packet(soc, soc_buffers)

            response = parse_packet(packet, client_info[soc])
            if packet == None:
                sockets.remove(soc)
                client_info.pop(soc)

            send_response(response, sockets, listener)


def main(argv):
    port = int(argv[1])
    run_server(port)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
