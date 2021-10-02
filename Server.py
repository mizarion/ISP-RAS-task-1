from socket import *

serverPort = 12011
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while 1:
    connectionSocket, addr = serverSocket.accept()
    ip, port = connectionSocket.getpeername()
    connectionSocket.send(ip.encode())
    connectionSocket.send(str(port).encode())
    connectionSocket.close()
