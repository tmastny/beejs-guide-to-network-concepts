import time
import calendar
import socket

address = "time.nist.gov"
port = 37

s = socket.socket()
s.connect((address, port))

req = ["GET / HTTP/1.1", f"Host: {address}:{port}", "Connection: close"]

req = "\r\n".join(req) + "\r\n"
req = req.encode()

s.sendall(req)

output = b""
while True:
    d = s.recv(1024)
    if len(d) == 0:
        break
    output += d

s.close()

# ne: time measured in nist epoch
# ue: time measured in unix epoch
nist_time_ne = int.from_bytes(output)

nist_epoch_ue = time.strptime("1 Jan 1900 00:00 UTC", "%d %b %Y %H:%M %Z")

unix_epoch_ne = calendar.timegm(nist_epoch_ue) * -1
sys_time_ue = calendar.timegm(time.gmtime())
sys_time_ne = int(unix_epoch_ne + sys_time_ue)

print(f"NIST time  : {nist_time_ne}")
print(f"System time: {sys_time_ne}")

nist_time_ue = nist_time_ne - unix_epoch_ne
data = [("NIST time  :", nist_time_ue), ("System time:", sys_time_ue)]

for label, etime in data:
    formatted_time = time.strftime("%d %b %Y %H:%M %Z", time.gmtime(etime))
    print(f"{label} {formatted_time}")
