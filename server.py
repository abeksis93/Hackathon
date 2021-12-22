import socket
import threading
from scapy.all import *

class Server:
    def __init__(self):
        # self.ip = scapy.get_if_addr("eth1")
        self.port = "SERVER_PORT"
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)


    def broadcast_to_clients(self):
        pass





# def main():
#     print("hello server")
#     print(get_if_addr("eth0"))

# if __name__ == '__main__':
#     main()
