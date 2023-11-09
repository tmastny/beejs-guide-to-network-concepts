ip = "198.51.100.10"
ip_int = [int(n) for n in ip.split(".")]

sum = 0
for i, n in enumerate(reversed(ip_int)):
    sum |= n << i * 8
