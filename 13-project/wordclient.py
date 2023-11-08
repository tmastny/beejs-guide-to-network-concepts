from typing import Union
import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2
RECV_SIZE = 5


def usage():
    print("usage: wordclient.py server port", file=sys.stderr)


packet_buffer = b""


def get_word_from_buffer(buffer: bytes) -> Union[bytes, None]:
    if len(buffer) < 2:
        return None

    nbytes = int.from_bytes(buffer[0:2]) + 2

    # why not just extract the word here? with range(2, ...)
    word = b""
    for i in range(min(len(buffer), nbytes)):
        word += buffer[i : i + 1]

    if len(word) == nbytes:
        return word

    return None


def get_next_word_packet(s: socket.socket):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer

    while True:
        if word := get_word_from_buffer(packet_buffer):
            packet_buffer = packet_buffer[len(word) :]
            return word

        packet_buffer += s.recv(RECV_SIZE)
        if packet_buffer == b"":
            return None


def extract_word(word_packet):
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    return word_packet[2:].decode()


# Do not modify:


def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
