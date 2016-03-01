# coding=utf-8
import socket, select

server = socket.socket()

host = socket.gethostname()
port = 1234
server.bind((host, port))

server.listen(5)
server.setblocking(0)
# epoll
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

epoll = select.epoll()
#epoll.register(server.fileno(), select.EPOLLIN)
#et模式
epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)
try:
    connections, requests, responses = {},{},{}
    while True:
        events = epoll.poll()
        for fd, event in events:
            # 新连接进来就交给epoll
            if fd == server.fileno():
                try:
                    #ET模式下，一直读，直到返回异常
                    while True:

                        connection, address = server.accept()
                        #设置socket为非阻塞
                        connection.setblocking(0)
                        epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)

                        # 放入队列
                        connections[connection.fileno()] = connection
                        requests[connection.fileno()] = b'request'
                        responses[connection.fileno()] = b'response'
                except socket.error:
                    pass

            # 如果发生一个读event，就读取从客户端发送过来的新数据。
            elif event & select.EPOLLIN:
                requests[fd] += connections[fd].recv(1024)
                # 检测到结束符则 注销对读event的关注，改为关注写event
                if EOL1 in requests[fd] or EOL2 in requests[fd]:
                    epoll.modify(fd, select.EPOLLOUT | select.EPOLLET)
                    # 打印请求
                    print '-' * 40, '\n', requests[fd].decode()
            # 如果发生写事件的处理
            elif event & select.EPOLLOUT:
                try:
                    #ET模式下写一直写，直到异常
                    while len(responses[fd]) > 0:
                        byteswritten = connections[fd].send(responses[fd])
                        responses[fd] = responses[fd][byteswritten:]
                except socket.error:
                    pass
                # 发完数据后shutdown，通知客户端 首先 关闭连接
                if len(responses[fd]) == 0:
                    # 不再关注
                    #转换为ET模式
                    epoll.modify(fd, select.EPOLLET)
                    # man socket.h 可以快速查看SHUT_RDWR之类缩写的意思
                    connections[fd].shutdown(socket.SHUT_RDWR)
                # HUP 表明客户端已经断开
                elif event & select.EPOLLHUP:
                    epoll.unregister(fd)
                    connections[fd].close()
                    del connections[fd]
finally:
    # 确保出错后能关闭socket
    epoll.unregister(server.fileno())
    epoll.close()
    server.close()
