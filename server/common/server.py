import socket
import logging
import signal

from .connection import ClientConnection

BET_SEPARATOR = "\t"

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_conns = []
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
                self._client_conns.append(client_conn)
                self.__handle_client_connection(client_conn)

        self.__close_sockets()

    def __close_sockets(self):
        """
        Close all active sockets
        """
        for client_conn in self._client_conns:
            client_conn.close()
        logging.info(f'action: close_sockets | result: success')

    def __handle_sigterm(self, signal, frame):
        """
        Handles a SIGTERM signal by stopping the server loop and closing its socket
        """
        logging.info("Signal SIGTERM received")
        self.active = False
        self._server_socket.close()

    def __handle_client_connection(self, client_conn):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        try:
            client_conn.receive_messages()
            logging.info(f'action: receive_all_bets | result: success | ip: {client_conn.client_addr[0]}')  
        except Exception as e:
            logging.info(str(e))              

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
        
