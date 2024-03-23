import socket
import logging
import signal

from .connection import ClientConnection

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
                client_conn = ClientConnection(client_sock, client_sock.getpeername())
                self.__handle_client_connection(client_conn)
        
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

    def __handle_client_connection(self, client_conn):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            bet_info = client_conn.receive_message()
            if not bet_info: return            
            self.__handle_client_bet(bet_info)
            if not client_conn.send_message(ACK_MESSAGE): return   
        except OSError as e:
            logging.error(f'action: receive_message | result: fail | error: {e}')
        finally:
            logging.info(f'action: close_connection | ip: {client_conn.client_addr[0]}')
            client_conn.close()
            
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
            logging.error('Error reading server socket')
            return None
        
