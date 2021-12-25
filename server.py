import socket
import threading
from scapy.all import *
from termcolor import *
import random
import operator

# SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_IP = get_if_addr('eth1')
SERVER_TCP_PORT = 26262
DEST_UDP_PORT = 13117
FORMAT = 'utf-8'
TCP_ADDRESS = (SERVER_IP, SERVER_TCP_PORT)
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
    '''
    A class representing a server with 2 sockets: UDP and TCP
    allowing communication with a client for a simple math problems game
    '''

    def __init__(self):
        """ initiate 2 sockets: UDP and TCP and set IP address"""       
        self.ip = SERVER_IP
        try:
            socket.inet_aton(self.ip)
        except:
            print("There was a problem trying to get the server's IP address.")
        self.tcp_port = SERVER_TCP_PORT
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print("There is a problem with the server's UPD socket.")
        try:
            self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("There is a problem with the server's TCP socket.")
        self.broadcasting = False
        self.available = True
        self.clients = {}

    def start(self):
        """ bind the sockets to the server and start listening for connection requests """
        self.udp_socket.bind(UDP_ADDRESS)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.welcome_socket.bind(TCP_ADDRESS)
        self.welcome_socket.listen(1)
        print("Server started, listening on IP address {}\n".format(SERVER_IP))
        self.thread_handler()
        self.welcome_socket.close()
        self.udp_socket.close()


    def stop(self):
        """ stop the server """
        self.welcome_socket.close()
        self.udp_socket.close()

    def thread_handler(self):
        """ handeling broadcasting and listening in multithreading """
        broadcast_thread = threading.Thread(target=self.broadcast_handler)
        listen_thread = threading.Thread(target=self.client_handler)
        broadcast_thread.start()
        listen_thread.start()
        listen_thread.join()
        broadcast_thread.join()


    def client_handler(self):
        """
        accept only 2 clients per game
        """
        while self.broadcasting:
            if len(self.clients) == 2:
                break
            else:
                try:
                    new_tcp_socket, address = self.welcome_socket.accept()
                    client_details = (new_tcp_socket, address)
                    client_name = new_tcp_socket.recv(1024).decode().strip('\n')
                    print(f'Team {client_name} has connected to server!')
                    self.clients[client_name] = client_details
                except:
                    continue 
         

    def broadcast_handler(self):
        """
        send offers to connect to clients
        """
        message = struct.pack('Ibh', MAGIC_COOKIE, MESSAGE_TYPE, self.tcp_port)
        max_time = time.time() + 10
        self.broadcasting = True
        while time.time() < max_time:
            address = ('<broadcast>', DEST_UDP_PORT)
            self.udp_socket.sendto(message, address)
            time.sleep(1)
        self.broadcasting = False


    def competition(self):
        """
        
        """
        answer, question = self.question_generator()
        player1 = self.clients.keys()[0]
        player2 = self.clients.keys()[1]
        message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can:\n{}".format(player1, player2, question)
        try:
            self.tcp_socket.send(message.encode())
        except:
            print("socket connection broken")
        max_time = time.time() + 10
        while time.time() < max_time:
            handle_client1 = threading.Thread(target=self.competition_handler, args=(self.clients.keys()[0], answer))
            handle_client2 = threading.Thread(target=self.competition_handler, args=(self.clients.keys()[1], answer))
            handle_client1.start()
            handle_client2.start()
            handle_client1.join(10)
            handle_client2.join(10)
            if handle_client1.is_alive() and handle_client2.is_alive():
                print("Game over!\nThe correct answer was {}!\nIt's a draw!".format(answer))
                break
                
    
    def competition_handler(self, client_name, answer):
        """
        
        """
        message = self.clients[client_name][0].recv(1024).decode().strip('\n')
        if message == answer:
            print("Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, client_name))
        else:
            for i in range(len(self.clients.keys())):
                if self.clients[i] != client_name:
                    print("Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, self.clients[i]))
                    break
        

    
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


# def main():
    # print("hello server")
    # print(get_if_addr(conf.iface)) # This is actually great

if __name__ == '__main__':
    # main()
    Server()
