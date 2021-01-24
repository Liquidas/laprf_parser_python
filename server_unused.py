import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((socket.gethostname(), 1234))
#s.bind((socket.gethostname(), 1234))

###reachable from any IP
s.bind(('', 1234))

#s.bind(('192.168.1.10', 1234))
#s.bind(('192.168.1.10:139', 1234))
#s.bind('192.168.1.10:139')
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.bind(('', 139))
s.listen(5)

while True:
    # now our endpoint knows about the OTHER endpoint.
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")
    #clientsocket.send(bytes("Hey there!!!","utf-8"))