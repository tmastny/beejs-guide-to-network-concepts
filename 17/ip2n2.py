ip = "198.51.100.10"

ipb = b"".join([(int(n)).to_bytes() for n in ip.split(".")])

print(int.from_bytes(ipb))
