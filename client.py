import socket
import threading
from scapy.all import *
import getch
import sys, termios, tty, time, threading, random

CLIENT_IP = get_if_addr('eth1')
CLIENT_UDP_PORT = 13117
CLIENT_TCP_PORT = 2026
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
BUFFER = 1024


class Client:
    '''
    A class representing a client with 2 sockets: UDP and TCP
    allowing communication with a server for a simple math problems game
    '''

    def __init__(self):
        """ initiate 2 sockets: UDP and TCP for communication with server"""
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
        self.client_name = "Robotrix"
        self.available = True
        self.wasStopped = False


    def start(self):
        """ bind the udp socket to the server and connect to the server via tcp socket """
        print("Client started, listening for offer requests...")
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(('', CLIENT_UDP_PORT))
        while True:
            try:
                packed_message, server_address = self.udp_socket.recvfrom(1024)
                magic_cookie, message_type, server_port = struct.unpack('Ibh', packed_message)
                if magic_cookie != MAGIC_COOKIE or message_type != MESSAGE_TYPE:
                    continue
                if server_port != 12026:
                    continue
                server_socket = (server_address[0], server_port)
                try:
                    self.tcp_socket.connect(server_socket)
                    print("Successfully connected to the server. Server's IP address: " + server_address[0])
                except:
                    print("Failed to connect to the server.")
                try:
                    print("Client trying to send name to the server.")
                    self.tcp_socket.send((self.client_name + "\n").encode())
                    print("Client sent name to the server.")
                except:
                    print("Client couldn't send name to the server.")
                    self.stop()
                    self.wasStopped = True
                    break
                try:
                    message = self.tcp_socket.recv(BUFFER).decode()
                    print(message)
                except:
                    break
                break
            except:
                continue
        

    def quick_math(self):
        """
        send an answer from client to server 
        """
        try:
            

            def getchar():
            # Return a single character from stdin.

                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

            answer = getchar()#getch.getch() #sys.stdin.readline()
            print("your answer was: {}".foramt(str(answer)))
            time.sleep(5)
            print("before encode")
            encoded_ans = str(answer).encode()
            self.tcp_socket.sendall(encoded_ans)
            print("after encode")
            time.sleep(5)

        finally:
            result = self.tcp_socket.recv(BUFFER).decode()
            print(result)
            self.stop() # stop after finishing the game
            self.wasStopped = True

    def stop(self):
        """
        stop the cient
        """
        if self.wasStopped == False:
            self.tcp_socket.close()
            self.udp_socket.close()


def main():
    while True:
        client = Client()
        client.start()
        try:
            client.quick_math()
            time.sleep(1)
        finally:
            client.stop()
            continue


if __name__ == '__main__':
    main()

