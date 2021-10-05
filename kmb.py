"""
Task-1 Клиент-серверное приложение
"""
import argparse
import logging
# import multiprocessing
from socket import SOCK_DGRAM
from socket import SOCK_STREAM
from socket import AF_INET
from socket import socket


def run_server(port, connection_protocol, logger):
    """
    Запускает сервер
    :param port: номер порта
    :param connection_protocol: протокол передачи данных (TCP | UDP)
    :param logger: Логер
    """
    connection_type = 'UDP' if connection_protocol == SOCK_DGRAM else 'TCP'
    logger(f"Running {connection_type} server....")
    server_socket = socket(AF_INET, connection_protocol)
    server_socket.bind(('', port))
    logger("The server is ready to receive")
    if connection_protocol == SOCK_DGRAM:  # if UDP
        while 1:
            client_address = server_socket.recvfrom(2048)[1]
            logger(f"[{connection_type}_Server]: " +
                   "New client {client_address} has connected. Start shipping...")
            host, port = client_address
            server_socket.sendto(host.encode(), client_address)
            server_socket.sendto(str(port).encode(), client_address)
            logger(f"[{connection_type}_Server]: Finished. Wait for a new client.")
    else:
        server_socket.listen(1)
        while 1:
            connection_socket = server_socket.accept()[0]
            host, port = connection_socket.getpeername()
            logger(f"[{connection_type}_Server]: " +
                   "New client ({host}:{port}) has connected. Start shipping.")
            connection_socket.send(host.encode())
            connection_socket.send(str(port).encode())
            logger(f"[{connection_type}_Server]: Finished. " +
                   "Close the connection and wait for a new client.")
            connection_socket.close()


def run_client(host, port, protocol, logger):
    """
    Запускает клиента
    :param host: Хост
    :param port: Номер порта
    :param protocol: протокол передачи данных (TCP | UDP)
    :param logger: Логер
    """
    client_socket = socket(AF_INET, protocol)
    connection_type = "UDP" if protocol == SOCK_DGRAM else "TCP"
    if protocol == SOCK_DGRAM:  # if UDP
        client_socket.sendto('hi'.encode(), (host, port))
        logger(f"[{connection_type}_Client]: Connect to the {host}:{port}")
        host = client_socket.recvfrom(1024)[0].decode()
        port = client_socket.recvfrom(1024)[0].decode()
        logger(f'[{connection_type}_Client]: Received a response from the server: {host}:{port}')
    else:
        client_socket.connect((host, port))
        logger(f"[{connection_type}_Client]: Connect to the {host}:{port}")
        host = client_socket.recv(1024).decode()
        port = client_socket.recv(1024).decode()
        logger(f'[{connection_type}_Client]: Received a response from the server: {host}:{port}')
        client_socket.close()
        logger(f"[{connection_type}_Client]: Closed the connection")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='хост (ip адрес) сервера')
    parser.add_argument('port', help='номер порта сервера')
    parser.add_argument('-s', dest='s', action='store_true', help='запуск в режиме сервера')
    # TCP | UDP
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', dest='t', action='store_true', help='связь по протоколу TCP')
    group.add_argument('-u', dest='u', action='store_true', help='связь по протоколу UDP')
    # LOGGING
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-o', dest='o', action='store_true', help='логирование в стандартный вывод')
    group.add_argument('-f', dest='f', help='логирование в файл <file>')

    args = parser.parse_args()

    # Choosing protocol
    PROTOCOL = SOCK_STREAM if args.t else SOCK_DGRAM

    # LOGGER
    log = print
    if not args.o:
        logging.basicConfig(filename=args.f + '.log', level=logging.INFO)
        log = logging.info

    # Run Server
    if args.s:
        try:
            run_server(int(args.port), PROTOCOL, log)
        except OSError:
            print("Сервер с такими параметрами уже запущен")

    # Run Client
    else:
        try:
            run_client(args.host, int(args.port), PROTOCOL, log)
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу с переданными параметрами")
        except ConnectionResetError:
            print("Не удалось подключиться к серверу с переданными параметрами")
