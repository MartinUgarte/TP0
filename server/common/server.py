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
                process = Process(target=self.__handle_client_connection, args=(client_conn, tx, write_lock))
                self._processes.append(process)
                process.start()
                agency_number = rx.recv()
                self._client_conns[agency_number] = client_conn

                if len(self._client_conns) == AGENCIES:
                    self.handle_draw()
                    break

        self.join_processes()
    
    def handle_draw(self):
        logging.info(f'action: sorteo | result: success')

        winners = self.__find_winners()

        if not self.__send_winners(winners):
            return
        
        logging.info(f'action: send_winners | result: success')

    def join_processes(self): 
        """
        Join active processes
        """
        for process in self._processes:
            process.join()
        logging.info(f'action: join_processes | result: success')  

    def __handle_sigterm(self, signal, frame):
        """
        Handles a SIGTERM signal by stopping the server loop and closing its socket
        """
        logging.info("action: sigterm_received | result: success")
        self._active = False
        self._server_socket.close()
        for client_conn in self._client_conns.values():
            client_conn.close()
        
    def __send_all_bets_ack(self, client_conn):
        message = f'{len(ALL_BETS_ACK)}{HEADER_SEPARATOR}{ALL_BETS_ACK}'
        if not client_conn.send_message(message): 
            return False
        logging.info(f'action: send_all_bets_ack | result: succes | ip: {client_conn.client_addr[0]}')
        return True
    
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
            try:
                message = f'{len(winner.document)}{HEADER_SEPARATOR}{winner.document}'
                self._client_conns[winner.agency].send_message(message)
            except:
                logging.error(f'Error sending winner to agency {winner.agency}')
                return False
        
        for agency_num, client_conn in self._client_conns.items():
            try:
                message = f'{len(END_WINNERS_ACK)}{HEADER_SEPARATOR}{END_WINNERS_ACK}'
                client_conn.send_message(message)
            except:
                logging.error(f'Error sending ACK winner to agency {agency_num}')
                return False
            client_conn.close()

        return True
    
    def __handle_client_connection(self, client_conn, tx, write_lock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        try:
            agency_number = client_conn.receive_messages(write_lock)          
            logging.info(f'action: receive_all_bets | result: success | ip: {client_conn.client_addr[0]}')   

            if self.__send_all_bets_ack(client_conn):
                tx.send(agency_number)

        except OSError as e:
            logging.error(f'action: receive_message | result: fail | error: {e}')
            client_conn.close()
        
        finally:
            return False
            
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
        