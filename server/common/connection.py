import logging

from .utils import process_bets, store_bets

HEADER_SEPARATOR = "#"
FLAG_SEPARATOR = ","
CHUNK_ACK = "CHUNK_ACK"
MAX_PAYLOAD_SIZE = 7996 # 8kB - 4B del header

class ClientConnection:

    def __init__(self, socket, addr):
        self.client_sock = socket
        self.client_addr = addr

    def receive_messages(self):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        
        size, end, message = self.receive_message()
        
        while not int(end):    
            full_message = self.avoid_short_read(message, size)
            bets = process_bets(full_message)
            store_bets(bets)
            self.send_message(CHUNK_ACK)
            size, end, message = self.receive_message()
        
        if message:
            full_message = self.avoid_short_read(message, size)
            bets = process_bets(full_message)
            store_bets(bets)

    def receive_message(self):
        size, flag = self.read_header()
        chunk = self.client_sock.recv(MAX_PAYLOAD_SIZE).decode('utf-8')   

        if not chunk:
            logging.error('action: receive_chunk | result: fail | error while reading socket')
            return
        return size, flag, chunk

    def read_header(self):
        message = ""
        read = self.client_sock.recv(1).decode('utf-8') 
        while read != HEADER_SEPARATOR:
            message += read
            read = self.client_sock.recv(1).decode('utf-8')
        header, flag = message.split(FLAG_SEPARATOR)
        return header, flag

    def avoid_short_read(self, message, header):
        size = int(header)
        full_message = message.encode('utf-8')

        while len(full_message) < size:
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

        return True
    
    def close(self):
        self.client_sock.close()