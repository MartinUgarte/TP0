import socket
import logging
import signal

from .utils import Bet, store_bets

BET_SEPARATOR = "\t"
ACK_MESSAGE = "ACK"

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.active = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        signal.signal(signal.SIGTERM, self.__handle_sigterm)

        while self.active:
            client_sock = self.__accept_new_connection()
            if self.active:
                self.__handle_client_connection(client_sock)
        
    def __handle_sigterm(self, signal, frame):
        """
        Handles a SIGTERM signal by stopping the server loop and closing its socket
        """
        logging.info("Signal SIGTERM received")
        self.active = False
        self._server_socket.close()

    def __handle_client_bet(self, bet_info):
        """
        Receives a bet from a client and stores it in the database
        """
        agency, name, surname, document, birthday, number = bet_info.split(BET_SEPARATOR)
        bet = Bet(agency, name, surname, document, birthday, number)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: ${document} | numero: ${number}')

    def receive_client_message(self, client_sock):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        header = client_sock.recv(3)
        if not header:
            logging.info('action: receive_message | result: fail | error while reading socket')
            return

        size = int(header.rstrip().decode('utf-8'))
        msg = ""

        while len(msg) < size:
            chunk = client_sock.recv(size - len(msg))
            if not chunk:
                logging.info('action: receive_message | result: fail | error while reading socket')
                return None
            msg += chunk.decode('utf-8')
        
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg.rstrip()}')

        return msg.rstrip()
    
    def send_message_to_client(self, client_sock, message):
        """
        Sends an ACK message to a specific client socket avoiding short-writes
        """
        total_sent = 0

        while total_sent < len(message):
            sent = client_sock.send(f'{message[total_sent:]}\n'.encode('utf-8'))
            if sent == 0:
                logging.info('action: send_ack | result: fail | error while sending message')
                return False
            total_sent += sent
        
        addr = client_sock.getpeername()
        logging.info(f'action: send_message | result: success | ip: {addr[0]} | msg: {message}')

        return True

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            bet_info = self.receive_client_message(client_sock)
            if not bet_info:
                return
                        
            self.__handle_client_bet(bet_info)

            if not self.send_message_to_client(client_sock, ACK_MESSAGE):
                return
            
        except OSError as e:
            logging.info(f'action: receive_message | result: fail | error: {e}')
        finally:
            client_sock.close()
            logging.info('action: socket closed')
            
    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except:
            logging.info('Error reading server socket')
            return None
        
