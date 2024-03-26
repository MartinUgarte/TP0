import socket
import logging
import signal

from .connection import ClientConnection

from .utils import load_bets, has_won

BET_SEPARATOR = "\t"
ALL_BETS_ACK = "ALL_BETS_ACK"
END_WINNERS_ACK = "END_WINNERS_ACK"
AGENCIES = 5
HEADER_SEPARATOR = "#"

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_conns = {}
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

    def __close_sockets(self):
        """
        Close all active sockets
        """
        for client_conn in self._client_conns.values():
            client_conn.close()
        logging.info(f'action: close_sockets | result: success')
        
    def __handle_sigterm(self, signal, frame):
        """
        Handles a SIGTERM signal by stopping the server loop and closing its socket
        """
        logging.info("Signal SIGTERM received")
        self.active = False
        self._server_socket.close()
        self.__close_sockets()

    def __find_winners(self):
        """
        Returns the lottery winners
        """
        winners = []
        for bet in load_bets():
            if has_won(bet):
                winners.append(bet)
        logging.info(f'action: sorteo | result: success')
        return winners

    def __send_winners(self, winners):
        """
        Sends the winners to all clients
        """

        for winner in winners:
            message = f'{len(winner.document)}{HEADER_SEPARATOR}{winner.document}'
            if not self._client_conns[winner.agency].send_message(message):
                logging.error(f'Error sending winner to agency {winner.agency}')
                return False
        
        for agency_num, client_conn in self._client_conns.items():
            message = f'{len(END_WINNERS_ACK)}{HEADER_SEPARATOR}{END_WINNERS_ACK}'
            if not client_conn.send_message(message):
                logging.error(f'Error sending END_WINNERS ACK to agency {agency_num}')
                return False                

        logging.info(f'action: send_winners | result: success')

        return True
    
    def __handle_client_connection(self, client_conn):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        agency_number = client_conn.receive_messages()

        if not agency_number:
            logging.info(f'action: receive_all_bets | result: fail | ip: {client_conn.client_addr[0]}')
            return 
        
        logging.info(f'action: receive_all_bets | result: success | ip: {client_conn.client_addr[0]}')

        self._client_conns[agency_number] = client_conn

        if len(self._client_conns) != AGENCIES:
            return
        
        winners = self.__find_winners()
        self.__send_winners(winners)
  
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
        