from re import S
import socket
import threading
from scapy.all import *
from termcolor import *
import random
import operator
import queue

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_TCP_PORT = 12026
DEST_UDP_PORT = 13117
FORMAT = 'utf-8'
TCP_ADDRESS = (SERVER_IP, SERVER_TCP_PORT)
UDP_ADDRESS = (SERVER_IP, DEST_UDP_PORT)
# UDP_ADDRESS = ('', DEST_UDP_PORT)
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
        self.clients_answers = {}

    def start(self):
        """ bind the sockets to the server and start listening for connection requests """
        self.udp_socket.bind(UDP_ADDRESS)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.welcome_socket.bind(TCP_ADDRESS)
        self.welcome_socket.listen(1)
        self.welcome_socket.settimeout(3)
        print("Server started, listening on IP address {}\n".format(SERVER_IP))
        self.thread_handler()
        self.udp_socket.close()
        self.welcome_socket.close()
        


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
        i=0
        while self.broadcasting:
            if len(self.clients) == 2:
                break
            else:
                i += 1
                try:
                    new_tcp_socket, address = self.welcome_socket.accept()
                    client_details = (new_tcp_socket, address)
                    client_name = new_tcp_socket.recv(1024).decode().strip('\n')
                    print("Team " + str(client_name) + " has connected to server!")
                    self.clients[client_name] = client_details
                    
                except:
                    continue 
        # print(self.clients)
         

    def broadcast_handler(self):
        """
        send offers to connect to clients
        """
        message = struct.pack('Ibh', MAGIC_COOKIE, MESSAGE_TYPE, self.tcp_port)
        max_time = time.time() + 10
        self.broadcasting = True
        while time.time() < max_time:
            self.udp_socket.sendto(message, ('<broadcast>', DEST_UDP_PORT))
            time.sleep(0.1)
        self.broadcasting = False


    # def competition(self):
    #     """
        
    #     """
    #     answer, question = self.question_generator()
    #     lst = list(self.clients.keys())
    #     player1 = lst[0]
    #     player2 = lst[1]
    #     player1_socket = list(self.clients[player1])[0]
    #     player2_socket = list(self.clients[player2])[0]
    #     message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can:\n{}".format(player1, player2, question)
    #     handle_client1 = threading.Thread(target=self.competition_handler, args=(player1, message, answer,))
    #     handle_client1.start()
    #     handle_client2 = threading.Thread(target=self.competition_handler, args=(player2, message, answer,))
    #     handle_client2.start()

       
    #     try:
    #         # self.welcome_socket.send(message.encode())
    #         # self.clients[pla]
    #         player1_socket.send(message.encode())
    #         player2_socket.send(message.encode())
    #     except:
    #         print("socket connection broken")
    #     max_time = time.time() + 10
    #     while time.time() < max_time:

    #         handle_client1.join()
    #         handle_client2.join()
    #         print("self.clients_answers: ", self.clients_answers)
    #         if handle_client1.is_alive() and handle_client2.is_alive():
    #             print("Game over!\nThe correct answer was {}!\nIt's a draw!".format(answer))
    #             break

    def competition(self):
        """
        
        """
        answer, question = self.question_generator()
        lst = list(self.clients.keys())
        player1 = lst[0]
        player2 = lst[1]
        player1_socket = list(self.clients[player1])[0]
        player2_socket = list(self.clients[player2])[0]

        message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can:\n{}".format(player1, player2, question)
        try:
            # self.welcome_socket.send(message.encode())
            # self.clients[pla]
            player1_socket.send(message.encode())
            player2_socket.send(message.encode())
        except:
            print("socket connection broken")
        # max_time = time.time() + 10
        # while time.time() < max_time:
        handle_client1 = threading.Thread(target=self.competition_handler, args=(player1, answer,))
        handle_client2 = threading.Thread(target=self.competition_handler, args=(player2, answer,))
        handle_client1.start()
        handle_client2.start()
        handle_client1.join(10)
        handle_client2.join(10)
        print("self.clients_answers: ", self.clients_answers)

        # if handle_client1.is_alive() and handle_client2.is_alive():
        if len(self.clients_answers) == 0:
            result = "Game over!\nThe correct answer was {}!\nIt's a draw!".format(answer)
            # break
        elif int(list(self.clients_answers.values())[0]) == answer:
            result = "Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, list(self.clients_answers.keys())[0])
            # break
        elif len(self.clients_answers) >= 2:
            if int(list(self.clients_answers.values())[1]) == answer:
                result = "Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, list(self.clients_answers.keys())[1])
                # break
            else:
                for i in range(len(self.clients.keys())):
                    if list(self.clients.keys())[i] != list(self.clients_answers.keys())[i]:
                        result = "Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, list(self.clients.keys())[i])
                        break
        print(result)
        player1_socket.send(result.encode())
        player2_socket.send(result.encode())
        player1_socket.close()
        player2_socket.close()
        self.clients = {}
        self.clients_answers = {}

        print("end of competition")
    
    def competition_handler(self, client_name, answer):
        """
        
        """
        try:
            message = self.clients[client_name][0].recv(1024).decode()
        except:
            message = ''
        if message == '':
            return
        else:
            self.clients_answers[client_name] = message.strip('\n')
        return
        # return answer
        # if message == answer:
        #     print("Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, client_name))
        # else:
        #     for i in range(len(self.clients.keys())):
        #         if list(self.clients.keys())[i] != client_name:
        #             print("Game over!\nThe correct answer was {}!\nCongratulations to the winner: {}".format(answer, list(self.clients.keys())[i]))
        #             break
        

    
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


def main():
    print("hello server")
    # print(get_if_addr(conf.iface)) # This is actually great
    # print(get_if_addr("eth1"))
    while True:
        server = Server()
        print("Server instance created properly")
        try:
            print("Starting server...")
            server.start()
            print("Server started properly")
        except:
            print("Server failed trying to start")
            server.stop()
            continue
        try:
            print("Starting math competition...")
            server.competition()
            # time.sleep(8)
        except:
            print("error in competition")
            continue

if __name__ == '__main__':
    main()
    # Server()
