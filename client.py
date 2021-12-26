import socket
import threading
from scapy.all import *

CLIENT_IP = socket.gethostbyname(socket.gethostname())
CLIENT_UDP_PORT = 13117
CLIENT_TCP_PORT = 2026
# FORMAT = 'ASCI'
# ADDRESS = (CLIENT_IP, CLIENT_UDP_PORT)
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2

class Client:
    def __init__(self):
        """
        explain this shit
        """
        self.ip = CLIENT_IP
        # self.ip = "132.72.202.2"
        try:
            socket.inet_aton(self.ip)
        except:
            print("There was a problem trying to get the client's IP address.")
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print("There is a problem with the client's UPD socket.")
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("There is a problem with the client's TCP socket.")
        self.client_name = "BotNet"
        self.available = True

    def start(self):
        """
        explain this shit
        """
        print("Client started, listening for offer requests...")
        self.udp_socket.bind(('0.0.0.0', CLIENT_UDP_PORT))
        # packed_message, server_address = self.udp_socket.recvfrom(1024)
        # print(server_address)
        # print(packed_message)
        while True:
            try:
                packed_message, server_address = self.udp_socket.recvfrom(1024)
                magic_cookie, message_type, server_port = struct.unpack('Ibh', packed_message)
                if magic_cookie != MAGIC_COOKIE or message_type != MESSAGE_TYPE:
                    continue
                server_socket = (server_address[0], server_port)
                try:
                    self.tcp_socket.connect(server_socket)
                    print("Successfully connected to the server. Server's IP address: " + server_address[0])
                except:
                    print("Failed to connect to the server.")
                try:
                    self.tcp_socket.send((self.client_name + "\n").encode())
                except:
                    self.tcp_socket.close()
                    continue
                break
            except:
                continue
        self.udp_socket.close()

    

    def quick_math(self):
        """
        explain this shit
        """
        print("In quick math")
        # stop after finishing the game
        # self.stop() //UNCOMMENT AFTER IMPLEMENTATION
        
        pass


    def stop(self):
        """
        explain this shit
        """
        self.tcp_socket.close()

def main():
    while True:
        client = Client()
        client.start()
        try:
            client.quick_math()
            # sleep(5)
        except:
            # traceback.print_exc()
            continue
    # pass


if __name__ == '__main__':
    main()

