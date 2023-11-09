import sys

n = int(sys.argv[1])


ipb = b""
for i in range(3, -1, -1):
    ipb += ((n >> 8 * i) & 0xFF).to_bytes()

print(ipb.hex())
print(n.to_bytes(4).hex())

ip = ".".join([str(b) for b in n.to_bytes(4)])
print(ip)
