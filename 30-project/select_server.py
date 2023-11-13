# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select


def recieve(s: socket.socket):
    req = s.recv(1024)

    return req


def run_server(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("", port))
    s.listen()

    read_set = {s}

    while True:
        ready_to_read, _, _ = select.select(read_set, {}, {})

        for soc in ready_to_read:
            if soc == s:
                new_soc, new_addr = soc.accept()
                read_set.add(new_soc)

                print(f"{new_addr}: connected")
            else:
                req = recieve(soc)
                if len(req) == 0:
                    print(f"{soc.getpeername()}: disconnected")
                    soc.close()
                    read_set.remove(soc)
                else:
                    print(f"{soc.getpeername()} {len(req)} bytes: {req}")


# --------------------------------#
# Do not modify below this line! #
# --------------------------------#


def usage():
    print("usage: select_server.py port", file=sys.stderr)


def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
