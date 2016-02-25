import socket
i = 0
while 1:
    s = socket.socket()
    host = socket.gethostname()
    s.connect((host,1234))
    print i
    i += 1