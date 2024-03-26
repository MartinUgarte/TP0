import logging

from .utils import process_bet, store_bets

HEADER_SEPARATOR = "#"
MSG_ACK = "MSG_ACK"

class ClientConnection:

    def __init__(self, socket, addr):
        self.client_sock = socket
        self.client_addr = addr

    def receive_message(self):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        
        message = self.read_message()
        bet = process_bet(message)
        store_bets([bet])
        ack_message = f'{len(MSG_ACK)}{HEADER_SEPARATOR}{MSG_ACK}'
        self.send_message(ack_message)

        return bet.document, bet.number

    def read_message(self):
        """
        Returns the message payload
        """

        size  = self.read_header()
        chunk = self.client_sock.recv(size).decode('utf-8') 

        if not chunk:
            raise Exception('action: receive_chunk | result: fail | error while reading socket')
        
        return self.avoid_short_read(chunk, size)
    
    def read_header(self):
        """
        Reads the message header
        """

        message = ""
        read = self.client_sock.recv(1).decode('utf-8') 
        while read != HEADER_SEPARATOR:
            message += read
            read = self.client_sock.recv(1).decode('utf-8')
            if not read:
                raise Exception('action: read_header | result: fail | error while reading socket')
            
        return int(message)

    def avoid_short_read(self, message, size):
        """
        Avoids short read
        """
         
        full_message = message.encode('utf-8')

        while len(full_message) < size:
            chunk = self.client_sock.recv(size - len(full_message))
            if not chunk:
                raise Exception('action: incomplete_message | result: fail | error while reading socket')
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
                raise Exception('action: send_ack | result: fail | error while sending message')
            total_sent += sent
        
        addr = self.client_sock.getpeername()
        logging.info(f'action: send_message | result: success | ip: {addr[0]} | msg: {message}')
    
    def close(self):
        """
        Closes the client socket
        """

        self.client_sock.close()