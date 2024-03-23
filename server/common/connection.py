import logging

from .utils import process_bets, store_bets

HEADER_LEN = 4
HEADER_SEPARATOR = "#"
MAX_PACKAGE_SIZE = 8000
CHUNK_ACK = "CHUNK_ACK"

class ClientConnection:

    def __init__(self, socket, addr):
        self.client_sock = socket
        self.client_addr = addr

    def receive_messages(self):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        header, end, message = self.receive_message()
        logging.info(f'header: {header}, end: {end}, message: {message}')
        while not int(end):    
            full_message = self.avoid_short_read(message, header)
            logging.info(f'action: receive_message | result: success | ip: {self.client_addr[0]} | msg: {full_message}')
            bets = process_bets(full_message)
            store_bets(bets)
            self.send_message(CHUNK_ACK)
            header, end, message = self.receive_message()
        
        if message:
            full_message = self.avoid_short_read(message, header)
            logging.info(f'action: receive_message | result: success | ip: {self.client_addr[0]} | msg: {full_message}')
            bets = process_bets(full_message)
            store_bets(bets)

    def receive_message(self):
        chunk = self.client_sock.recv(MAX_PACKAGE_SIZE).decode('utf-8')   

        if not chunk:
            logging.error('action: receive_chunk | result: fail | error while reading socket')
            return
        return chunk.split(HEADER_SEPARATOR)

    def avoid_short_read(self, message, header):
        size = int(header)
        full_message = message.encode('utf-8')

        while len(full_message) < size:
            logging.info(f'action: incomplete_message | result: in_progress | ip: {self.client_addr[0]}')
            chunk = self.client_sock.recv(size - len(full_message))
            if not chunk:
                logging.error('action: incomplete_message | result: fail | error while reading socket')
                return None
            full_message += chunk

        return full_message.rstrip().decode('utf-8')

    def send_message(self, message):
        """
        Sends an ACK message to a specific client socket avoiding short-writes
        """
        total_sent = 0

        while total_sent < len(message):
            sent = self.client_sock.send(f'{message[total_sent:]}\n'.encode('utf-8'))
            if sent == 0:
                logging.error('action: send_ack | result: fail | error while sending message')
                return False
            total_sent += sent
        
        addr = self.client_sock.getpeername()
        logging.info(f'action: send_message | result: success | ip: {addr[0]} | msg: {message}')

        return True
    
    def close(self):
        self.client_sock.close()