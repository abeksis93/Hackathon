import socket
import threading
from scapy.all import *


SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 26262
DEST_UDP_PORT = 12026
FORMAT = 'ASCI'
ADDRESS = (SERVER_IP, SERVER_PORT)
MAGIC_COOKIE = "0xabcddcba"
MESSAGE_TYPE = "0x2"


class Server:
    def __init__(self):
        """
        explain this shit
        """        
        self.ip = SERVER_IP
        try:
            socket.inet_aton(self.ip)
        except:
            print("There was a problem trying to get the server's IP address.")
        self.port = SERVER_PORT
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print("There is a problem with the server's UPD socket.")
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("There is a problem with the server's TCP socket.")
        print(self.ip)
        self.broadcasting = False
        self.available = False

    def start(self):
        """
        explain this shit
        """
        self.udp_socket.bind(ADDRESS)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket.bind(ADDRESS)
        self.tcp_socket.listen(2)
        self.thread_handler()
        self.tcp_socket.close()
        self.udp_socket.close()


    def stop(self):
        """
        explain this shit
        """
        self.tcp_socket.close()
        self.udp_socket.close()

    def thread_handler(self):
        """
        explain this shit
        """
        broadcast_thread = threading.Thread(target=self.broadcast_handler)
        listen_thread = threading.Thread(target=self.client_handler)
        broadcast_thread.start()
        listen_thread.start()
        listen_thread.join()
        broadcast_thread.join()


    def client_handler(self):
        """
        explain this shit
        """
        pass

    def broadcast_handler(self):
        """
        explain this shit
        """
        message = struct.pack('Ibh', MAGIC_COOKIE, MESSAGE_TYPE, self.port)
        max_time = time.time() + 10
        self.broadcasting = True
        while time.time() < max_time:
            address = ('<broadcast>', DEST_UDP_PORT)
            self.udp_socket.sendto(message, address)
            # print(f'Broadcast message number {counter} sent')
            time.sleep(1)
        self.broadcasting = False

    def competition(self):
        pass

    
    def question_generator(self):
        pass

    def calculator(self):
        pass


# def main():
    # print("hello server")
    # print(get_if_addr(conf.iface)) # This is actually great

if __name__ == '__main__':
    # main()
    Server()
