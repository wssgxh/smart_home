# -*- coding: utf-8
import logging
import re
import socket
import threading
import time
from datetime import datetime

from config import UID, TOPIC
from operation import shutdown_pc


def setup_logger():
    log_file = "log/log_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message):
    logging.info(message)
    print(message)

    server_ip = 'bemfa.com'
    server_port = 8344


def connTCP():
    global tcp_client_socket
    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = 'bemfa.com'
    server_port = 8344

    try:
        with tcp_client_socket as s:
            s.connect((server_ip, server_port))
            substr = f'cmd=1&uid={UID}&topic={TOPIC}\r\n'
            s.send(substr.encode("utf-8"))
    except Exception as e:
        logging.exception(f"Error connecting to server: {e}")
        time.sleep(2)
        connTCP()


def Ping():
    try:
        keeplive = 'ping\r\n'
        tcp_client_socket.send(keeplive.encode("utf-8"))
    except:
        time.sleep(2)
        connTCP()

    t = threading.Timer(30, Ping)
    t.start()


if __name__ == "__main__":
    setup_logger()
    connTCP()
    Ping()
    log('Listening ')

    while True:
        try:
            recvData = tcp_client_socket.recv(1024)
            if not len(recvData):
                continue

            logging.info(f'raw message received: {recvData}')
            match = re.search(b'msg=(.*?)\r\r\n', recvData)
            if match:
                message = match.group(1).decode('utf-8')
                log(f'message matched: {message}')

                if message == 'off':
                    log(f'action: PC shut down')
                    logging.shutdown()
                    shutdown_pc()
                    exit(0)

                if message == 'exit':
                    log(f'action: exit program')
                    logging.shutdown()
                    exit(0)

        except Exception as e:
            logging.error(f'Error: {str(e)}')
            logging.shutdown()
