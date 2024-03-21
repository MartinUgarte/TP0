import socket
import logging
import signal

from .utils import Bet, load_bets, store_bets

MSG_SEPARATOR = " "
BET_SEPARATOR = "\t"

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
        agency, name, surname, document, birthday, number = bet_info.split(BET_SEPARATOR)
        bet = Bet(agency, name, surname, document, birthday, number)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: ${document} | numero: ${number}')

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()

            logging.info(msg)
            size, bet_info = msg.split(MSG_SEPARATOR)

            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            self.__handle_client_bet(bet_info)
            client_sock.send("OK\n".encode('utf-8'))
            
            if len(msg) - 2 == int(size): # Check if the size is correct without the \n and the extra space
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                self.__handle_client_bet(bet_info)
                client_sock.send("OK\n".encode('utf-8'))
            else:
                logging.info(f'action: receive_message | result: fail | expected bytes: {size} | received bytes: {len(msg)}')

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

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
        
