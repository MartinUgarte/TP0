import logging

from .utils import process_bets, store_bets

HEADER_SEPARATOR = "#"
FLAG_SEPARATOR = ","
CHUNK_ACK = "CHUNK_ACK"

class ClientConnection:

    def __init__(self, socket, addr):
        self.client_sock = socket
        self.client_addr = addr

    def receive_messages(self):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        
        end, message = self.receive_message()

        agency = int(message[0])

        while not end:    
            self.process_message(message)
            end, message = self.receive_message()
        
        if message: self.process_message(message)
        
        return agency

    def process_message(self, message):
        """
        Decodes the message transforming it into bets and stores them
        """
        
        bets = process_bets(message)
        store_bets(bets)
        ack_message = f'{len(CHUNK_ACK)}{HEADER_SEPARATOR}{CHUNK_ACK}'
        self.send_message(ack_message)

    def receive_message(self):
        """
        Receives the message by separating it into header and payload
        """

        size, flag = self.read_header()
        chunk = self.client_sock.recv(size).decode('utf-8')   

        if not chunk:
            raise Exception('action: receive_chunk | result: fail | error while reading socket')
        return flag, self.avoid_short_read(chunk, size)

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
        size, flag = message.split(FLAG_SEPARATOR)
        return int(size), int(flag)

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
    
    def close(self):
        self.client_sock.close()