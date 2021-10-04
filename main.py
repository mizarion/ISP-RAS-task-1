import argparse
from socket import *

def run_server(port, protocol):
    serverSocket = socket(AF_INET, protocol)
    serverSocket.bind(('', port))
    serverSocket.listen(1)
    print('The server is ready to receive')
    while 1:
        connectionSocket, addr = serverSocket.accept()
        ip, port = connectionSocket.getpeername()
        connectionSocket.send(ip.encode())
        connectionSocket.send(str(port).encode())
        connectionSocket.close()


def run_client(host, port, protocol):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))
    # Получаем ответ от сервера
    ip = clientSocket.recv(1024).decode()
    port = clientSocket.recv(1024).decode()
    print(f'From Server: {ip}:{port}')
    clientSocket.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='хост (ip адрес) сервера')
    parser.add_argument('port', help='номер порта сервера')
    parser.add_argument('-s', dest='s', action='store_true', help='запуск программы в режиме сервера')

    # TCP | UDP
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', dest='t', action='store_true', help='связь по протоколу TCP')
    group.add_argument('-u', dest='u', action='store_true', help='связь по протоколу UDP')

    # LOGGING
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-o', dest='o', action='store_true', help='логирование в стандартный вывод')
    group.add_argument('-f', dest='f', help='логирование в файл <file>')

    args = parser.parse_args()

    print(args.host)
    print(args.port)
    print(f"s={args.s}")
    print(f"t={args.t}")
    print(f"u={args.u}")
    print(f"o={args.o}")
    print(f"f={args.f}")

    protocol = SOCK_STREAM if args.t else SOCK_DGRAM

    if (args.s):
        run_server(int(args.port), protocol)
    else:
        run_client(args.host, int(args.port), protocol)

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
