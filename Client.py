from socket import *

serverName = 'localhost'
serverPort = 12011
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
# Получаем ответ от сервера
ip = clientSocket.recv(1024).decode()
port = clientSocket.recv(1024).decode()
print(f'From Server: {ip}:{port}')
clientSocket.close()
