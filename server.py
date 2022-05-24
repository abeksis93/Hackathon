import socket
import threading
from scapy.all import *
import random
import operator
from stoppable_thread import StoppableThread

SERVER_IP = get_if_addr('eth1') #socket.gethostbyname(socket.gethostname())
SERVER_TCP_PORT = 12026
DEST_UDP_PORT = 13117
FORMAT = 'utf-8'
TCP_ADDRESS = (SERVER_IP, SERVER_TCP_PORT)
UDP_ADDRESS = (SERVER_IP, DEST_UDP_PORT)
# UDP_ADDRESS = ('', DEST_UDP_PORT)
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
BUFFER = 1024
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
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print("There is a problem with the server's UPD socket.")
        try:
            self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("There is a problem with the server's TCP socket.")
        self.broadcasting = False
        self.clients = {}
        self.clients_answers = {}
        self.threads = []
        self.game_mode = False
        self.ans = []


    def start(self):
        """ bind the sockets to the server and start listening for connection requests """
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(UDP_ADDRESS)
        self.welcome_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.welcome_socket.bind(TCP_ADDRESS)
        self.welcome_socket.listen(2)
        # self.welcome_socket.setblocking(0)
        self.welcome_socket.settimeout(10)
        print("Server started, listening on IP address {}\n".format(SERVER_IP))
        self.thread_handler()
        self.udp_socket.close()
        self.welcome_socket.close()
        

    def stop(self):
        """ stop the server """
        self.disconnect_clients()
        self.welcome_socket.close()
        self.udp_socket.close()
        

    def disconnect_clients(self):
        """
        This function disconnects all clients from the server.
        """
        for _, client_socket in self.clients.items():
            client_socket[0].close()

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
                    new_tcp_socket.setblocking(0)
                    client_details = (new_tcp_socket, address)
                    client_name = new_tcp_socket.recv(BUFFER).decode(FORMAT).strip('\n')
                    print("Player " + str(client_name) + " has connected to server!")
                    self.clients[client_name] = client_details 
                except:
                    continue 
        print(self.clients)
         

    def broadcast_handler(self):
        """
        send offers to connect to clients
        """
        message = struct.pack('Ibh', MAGIC_COOKIE, MESSAGE_TYPE, SERVER_TCP_PORT)
        max_time = time.time() + 10
        self.broadcasting = True
        while time.time() < max_time:
            self.udp_socket.sendto(message, ('<broadcast>', DEST_UDP_PORT))
            if len(self.clients) == 2:
                break
            time.sleep(1)
        self.broadcasting = False


    def competition(self):
        """
        starting the game, activating threads only if there are connections
        """
        self.game_mode = True
        answer, question = self.question_generator()
        lst = list(self.clients.keys())
        player1 = lst[0]
        player2 = lst[1]
        self.clients_answers[player1] = ''
        self.clients_answers[player2] = ''
        message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can:\n{}".format(player1, player2, question)
        for client in self.clients.keys():
            thread = threading.Thread(target=self.competition_handler, args=(client, message, answer,))
            self.threads.append(thread)
            thread.start()
            print("{} thread started".format(client))
        # if len(self.ans) > 0:
            # time.sleep(10)
        for t in self.threads:
            t.join()
        
        self.game_mode = False
        print("end of competition")
    

    def check_winning_group(self, client_name, answer):
        """
        check the winning group and return a game over message
        :return: The Game Over message
        """
        print("self.clients_answers: ", self.clients_answers)
        client_socket = list(self.clients[client_name])[0]
        ans_player1, ans_player2 = list(self.clients_answers.values())[0], list(self.clients_answers.values())[1]
        name_player1, name_player2 = list(self.clients_answers.keys())[0], list(self.clients_answers.keys())[1]
        result = "Game over!\nThe correct answer was {}!\n".format(answer)
        win_player1, win_player2 = "Congratulations to the winner: {}".format(name_player1), "Congratulations to the winner: {}".format(name_player2)
        if ans_player1 == '' and ans_player2 == '':
            result += "It's a draw!"
            # break
        elif ans_player1 != '' or ans_player2 == '':
            if int(float(ans_player1)) == answer:
                result += win_player1
            else:
                result += win_player2
        elif ans_player1 == '' or ans_player2 != '':
            if int(float(ans_player2)) == answer:
                result += win_player2
            else:
                result += win_player1
        client_socket.sendall(result.encode())
        client_socket.close()

    def overkill(self):
        for client in self.clients_answers.keys():
            if self.clients_answers[client] == None:
                self.clients_answers[client] = ''


    def competition_handler(self, client_name, question, answer):
        """
        {key: conn, value: (group_name, groupNumber)}
        """
        print("in competition_handler")
        client_socket = list(self.clients[client_name])[0]
        client_socket.send(question.encode())
        message = ''
        start_time = time.time()
        while self.game_mode and time.time() - start_time < 10:
            try:
                # print("in try before receive", client_name)
                # in_ans, _, _ = select([client_socket], [], [], 10)
                # print("in try after select", client_name)
                # if in_ans:
                    # print("in ans")
                # print(self.ans)
                message = client_socket.recv(BUFFER)#rstrip()
                
                if message == '':
                    continue
                else:
                    break
                tmp = message.decode()
                message = tmp
            except:
                print("in except")
                break
                # return
        print("message from " + str(client_name) + " in competition_handler. answer: " + str(message))
        self.clients_answers[client_name] = str(message) # str(self.ans[-1])
        # self.overkill()
        self.check_winning_group(client_name, answer)
        

    
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
    print("hello from server")
    while True:
        server = Server()
        print("Server instance created properly")
        try:
            print("Starting server...")
            server.start()
            # time.sleep(4)
            print("Server started properly")
        except:
            print("Server failed trying to start")
            server.stop()
            continue
        try:
            print("Starting math competition...")
            server.competition()
            # time.sleep(4)
        except:
            server.stop()
            print("error in competition")
            continue

if __name__ == '__main__':
    main()
    # Server()
