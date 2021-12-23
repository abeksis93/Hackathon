import socket
import threading
from scapy.all import *

CLIENT_IP = socket.gethostbyname(socket.gethostname())
CLIENT_UDP_PORT = 12026
CLIENT_TCP_PORT = 2026
# FORMAT = 'ASCI'
# ADDRESS = (CLIENT_IP, CLIENT_UDP_PORT)
MAGIC_COOKIE = "0xabcddcba"
MESSAGE_TYPE = "0x2"

class Client:
    def __init__(self):
        """
        explain this shit
        """
        self.ip = CLIENT_IP
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
        self.udp_socket.bind((CLIENT_IP, CLIENT_UDP_PORT))
        # packed_message, server_address = self.udp_socket.recvfrom(1024)
        # print(server_address)
        # print(packed_message)
        while True:
            try:
                packed_message, server_address = self.udp_socket.recvfrom(1024)
                message = struct.unpack('Ibh', packed_message) 
                magic_cookie = message[0]
                message_type = message[1]
                server_port = message[2]
                if magic_cookie != MAGIC_COOKIE or message_type != MESSAGE_TYPE:
                    continue
                print("Received offer from " + server_address[0] + ", attempting to connect...")
                try:
                    self.tcp_socket.connect(server_address[0], server_port)
                    print("Successfully connected to the server.\nServer's IP address: " + server_address[0])
                except:
                    print("Failed to connect to the server.")
                try:
                    self.tcp_socket.send(self.client_name + "\n")
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
        # stop after finishing the game
        # self.stop() //UNCOMMENT AFTER IMPLEMENTATION
        pass


    def stop(self):
        """
        explain this shit
        """
        self.tcp_socket.close()

def main():
    # while True:
    client = Client()
    client.start()
    # pass


if __name__ == '__main__':
    main()

