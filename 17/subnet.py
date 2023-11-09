import sys

ip = sys.argv[1]
ip, subnet_bits = ip.split("/")

ipb = b"".join([int(n).to_bytes(1) for n in ip.split(".")])
ipn = int.from_bytes(ipb)

mask = 0
for i in range(8 * 4):
    if i >= int(subnet_bits):
        mask <<= 1
    else:
        mask = (mask << 1) | 1

print(bin(mask))
print(int(mask).bit_count())


def dot(bytes):
    return ".".join([str(b) for b in bytes.to_bytes(4)])


print(dot(mask))

subnet = ipn & mask
subnet = dot(subnet)
print(subnet)

host = ipn & (~mask & 0xFFFFFFFF)
print(host)
