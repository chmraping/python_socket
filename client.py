import socket
import time
i = 0
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = socket.gethostname()
s.connect((host,1234))
#s.setblocking(0)
s.sendall('abcd')
s.sendall(b'\n\n')
data = ''
data = s.recv(1024)
print data
