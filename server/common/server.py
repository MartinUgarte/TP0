import socket
import logging
import signal

from .connection import ClientConnection
from multiprocessing import Process, Lock, Pipe

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
        self._active = True
        self._processes = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
    
        signal.signal(signal.SIGTERM, self.__handle_sigterm)
        write_lock = Lock()

        while self._active:
            client_sock = self.__accept_new_connection()
            
            if self._active:
                client_conn = ClientConnection(client_sock, client_sock.getpeername())
                rx, tx = Pipe()
                self.create_process(client_conn, tx, write_lock)
                agency_number = rx.recv()
                if not agency_number: break
                if self.add_client_conn(agency_number, client_conn):
                    self.handle_draw()
                    self._server_socket.close()
                    self.__close_sockets()
                    self._active = False

        self.join_processes()
    
    def __close_sockets(self):
        """
        Close all active sockets
        """

        for client_conn in self._client_conns.values():
            client_conn.close()
        logging.info(f'action: close_sockets | result: success')
        
    def create_process(self, client_conn, tx, write_lock):
        """
        Creates a new process to handle the new client connection
        """

        process = Process(target=self.__handle_client_connection, args=(client_conn, tx, write_lock))
        self._processes.append(process)
        process.start()

    def join_processes(self): 
        """
        Join active processes and close all sockets
        """
        for process in self._processes:
            process.join()
        logging.info(f'action: join_processes | result: success')  

    def __handle_sigterm(self, _signal, _frame):
        """
        Handles a SIGTERM signal by stopping the server loop and closing its socket
        """

        logging.info("action: sigterm_received | result: success")
        self._active = False
        self._server_socket.close()
        self.__close_sockets()

    def add_client_conn(self, agency_number, client_conn):
        """
        Add a client connection to a dictionary and returns True if it is the last one
        """

        self._client_conns[agency_number] = client_conn
        return len(self._client_conns) == AGENCIES

    def handle_draw(self):
        """
        Performs the draw, determines the winners and send the results to clients
        """

        winners = self.__find_winners()
        logging.info(f'action: sorteo | result: success')
        if not self.__send_winners(winners): return
        logging.info(f'action: send_winners | result: success')
            
    def __find_winners(self):
        """
        Returns the lottery winners
        """
        
        winners = []
        for bet in load_bets():
            if has_won(bet):
                winners.append(bet)
        return winners

    def __send_winners(self, winners):
        """
        Sends the winners to all clients
        """

        for winner in winners:
            message = f'{len(winner.document)}{HEADER_SEPARATOR}{winner.document}'
            self._client_conns[winner.agency].send_message(message)
        for client_conn in self._client_conns.values():
            message = f'{len(END_WINNERS_ACK)}{HEADER_SEPARATOR}{END_WINNERS_ACK}'
            client_conn.send_message(message)
        logging.info(f'action: send_winners | result: success')
        
    def __handle_client_connection(self, client_conn, tx, write_lock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        
        try:

            agency_number = client_conn.receive_messages(write_lock)      

            logging.info(f'action: receive_all_bets | result: success | ip: {client_conn.client_addr[0]}')   
                    
            self.__send_to_parent(agency_number, tx)

        except Exception as e:
            logging.error(str(e))
            self._server_socket.close()
            self.__close_sockets()
            self.__send_to_parent(None, tx)

    def __send_to_parent(self, message, tx):
        tx.send(message)
        tx.close()

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
        