import socket
import threading
from scapy.all import *
from termcolor import *
import random
import operator

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 26262
DEST_UDP_PORT = 12026
FORMAT = 'utf-8'
TCP_ADDRESS = (SERVER_IP, SERVER_PORT)
UDP_ADDRESS = (SERVER_IP, 20262)
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

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
        self.available = True

    def start(self):
        """
        explain this shit
        """
        self.udp_socket.bind(UDP_ADDRESS)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket.bind(TCP_ADDRESS)
        self.tcp_socket.listen(1)
        print("Server started, listening on IP address {}\n".format(SERVER_IP))
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
            time.sleep(1)
        self.broadcasting = False

    def competition(self):
        pass

    
    def question_generator(self):
        ops = {'+':operator.add,
           '-':operator.sub,
           '*':operator.mul,
           '/':operator.truediv}
        validQ = False
        while not validQ:
            op = random.choice(list(ops.keys()))
            if op == '*':
                num1 = random.randint(0,3)
                num2 = random.randint(0,3)   
            elif op == '/':
                num1 = random.randint(0,12)
                num2 = random.randint(1,10) # no 0's to protect against divide-by-zero
            elif op == '+':
                num1 = random.randint(0,4)
                num2 = random.randint(0,5)
            else: # op is -
                num1 = random.randint(0,11)
                num2 = random.randint(0,10)
            answer = ops.get(op)(num1,num2)
            if str(answer).isdigit():
                validQ = True
                question = 'What is {} {} {}?\n'.format(num1, op, num2)
        return answer, question

    def calculator(self):
        pass


# def main():
    # print("hello server")
    # print(get_if_addr(conf.iface)) # This is actually great

if __name__ == '__main__':
    # main()
    Server()
