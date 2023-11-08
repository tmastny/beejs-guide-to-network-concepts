def ip2b(ip) -> bytes:
    ipb = b""
    for num in ip.split("."):
        ipb += int(num).to_bytes()

    return ipb


def checksum(dat: bytes):
    if len(dat) % 2 == 1:
        dat += b"\x00"

    sum = 0
    for i in range(0, len(dat), 2):
        b = dat[i : i + 2]
        sum += int.from_bytes(b)
        sum = (sum & 0xFFFF) + (sum >> 16)

    return (~sum) & 0xFFFF


dir = "tcp_data"

for i in range(10):
    with open(f"{dir}/tcp_addrs_{i}.txt", mode="r") as f:
        line = f.read().strip()
        src_ip, des_ip = line.split(" ")

    with open(f"{dir}/tcp_data_{i}.dat", mode="rb") as f:
        tcp = f.read()

    # tcp len must be 2 bytes
    ip_header = ip2b(src_ip) + ip2b(des_ip) + b"\x00\x06" + len(tcp).to_bytes(2)

    recv_checksum = int.from_bytes(tcp[16:18])
    tcp0 = tcp[:16] + b"\x00\x00" + tcp[18:]

    calc_checksum = checksum(ip_header + tcp0)

    if recv_checksum == calc_checksum:
        print("PASS")
    else:
        print("FAIL")
