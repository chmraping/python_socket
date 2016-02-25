import socket,select
server = socket.socket()

host = socket.gethostname()
port = 1234
server.bind((host,port))

server.listen(5)

#epoll
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

epoll = select.epoll()
epoll.register(server.fileno,select.EPOLLIN)

events =epoll.poll()
connections,requests,responses = {}
for fd,event in events:
    #新连接进来就交给epoll
    if fd == server.fileno():
        connection,address = server.accept()
        epoll.register(connection.fileno,select.EPOLLIN)

        #放入队列
        connections[connection.fileno()] = connection
        requests[connection.fileno()] = b'request'
        responses[connection.fileno()] = b'response'

    #如果发生一个读event，就读取从客户端发送过来的新数据。
    elif event & select.EPOLLIN:
        requests[fd] += connections[fd].recv(1024)
        #检测到结束符则 注销对读event的关注，改为关注写event
        if EOL1 in requests[fd] or EOL2 in requests[fd]:
            epoll.modify(fd,select.EPOLLOUT)
            #打印请求
            print '-'*40,'\n',requests[fd].decode()
    #如果发生写事件的处理
    elif event & select.EPOLLOUT:
        byteswritten = connection[fd].send(responses[fd])
        responses[fd] = responses[fd][byteswritten:]
        #发完shutdown，通知客户端关闭连接
        if len(responses[fd]) == 0:
            #不再关注
            epoll.modify(fd,0)
            connections[fd].shutdown(socket.SHUT_RDWR)




while 1:
    client, address = server.accept()
    print 'welecome ',address
    client.send('thanks')
    client.close()