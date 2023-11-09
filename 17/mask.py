import sys

mask = b"".join([int(n).to_bytes(1) for n in sys.argv[1].split(".")])

print(int.from_bytes(mask).bit_count())
