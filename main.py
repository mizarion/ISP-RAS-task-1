import argparse
import logging
from socket import *
import multiprocessing


def create_logger(file_name):
    if (file_name == None):
        multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(processName)s|%(levelname)s] %(message)s')
    handler = logging.FileHandler(f'{file_name}.log')
    handler.setFormatter(formatter)
    if not len(logger.handlers):
        logger.addHandler(handler)
    return logger


def run_server(port, protocol, file_name):
    logger = create_logger(file_name).info
    prot = 'UDP' if protocol == SOCK_DGRAM else 'TCP'
    logger(f"Running {prot} server....")
    server_socket = socket(AF_INET, protocol)
    server_socket.bind(('', port))
    logger("The server is ready to receive")
    if (protocol == SOCK_DGRAM):  # if UDP
        while 1:
            message, client_address = server_socket.recvfrom(2048)
            logger(f"[{prot}_Server]: New client {client_address} has connected. Start shipping...")
            ip, port = client_address
            server_socket.sendto(ip.encode(), client_address)
            server_socket.sendto(str(port).encode(), client_address)
            logger(f"[{prot}_Server]: Finished. Wait for a new client.")
    else:
        server_socket.listen(1)
        while 1:
            connection_socket, addr = server_socket.accept()
            ip, port = connection_socket.getpeername()
            logger(f"[{prot}_Server]: New client ({ip}:{port}) has connected. Start shipping.")
            connection_socket.send(ip.encode())
            connection_socket.send(str(port).encode())
            logger(f"[{prot}_Server]: Finished. Close the connection and wait for a new client.")
            connection_socket.close()


def run_client(host, port, protocol, file_name):
    logger = create_logger(file_name).info
    client_socket = socket(AF_INET, protocol)
    prot = "UDP" if protocol == SOCK_DGRAM else "TCP"
    if (protocol == SOCK_DGRAM):  # if UDP
        client_socket.sendto('hi'.encode(), (host, port))
        logger(f"[{prot}_Client]: Connect to the {host}:{port}")
        ip = client_socket.recvfrom(1024)[0].decode()
        port = client_socket.recvfrom(1024)[0].decode()
        logger(f'[{prot}_Client]: Received a response from the server: {ip}:{port}')
    else:
        client_socket.connect((host, port))
        logger(f"[{prot}_Client]: Connect to the {host}:{port}")
        ip = client_socket.recv(1024).decode()
        port = client_socket.recv(1024).decode()
        logger(f'[{prot}_Client]: Received a response from the server: {ip}:{port}')
        client_socket.close()
        logger(f"[{prot}_Client]: Closed the connection")


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

    # Choosing protocol
    protocol = SOCK_STREAM if args.t else SOCK_DGRAM

    # Run Server
    if (args.s):
        # try:
        # run_server(int(args.port), protocol, args.f)
        run_server(int(args.port), protocol, args.f)
        # except OSError:
        #    print("Сервер с такими параметрами уже запущен")

    # Run Client
    else:
        try:
            # Если подключиться с другим протоколом (например UDP к TCP серверу), то можно зависнуть...
            # Попробывал решить эту проблему через вынесения в отдельный поток и контролем его времени жизни
            p = multiprocessing.Process(target=run_client, args=(args.host, int(args.port), protocol, args.f))
            p.start()
            p.join(10)  # думаю 10 секунд достаточно для пересылки сообщения
            if p.is_alive():
                print("Клиент до сих пор работает...")
                p.terminate()
                p.join()
                print("Работа клиента завершена")
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу с переданными параметрами")
