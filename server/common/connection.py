import logging

HEADER_LEN = 2

class ClientConnection:

    def __init__(self, socket, addr):
        self.client_sock = socket
        self.client_addr = addr

    def receive_message(self):
        """
        Read message from a specific client socket, avoiding short-reads
        """
        header = self.client_sock.recv(HEADER_LEN)
        
        if not header:
            logging.error('action: receive_message | result: fail | error while reading socket')
            return

        size = int(header.decode('utf-8'))
        msg = b''

        while len(msg) < size:
            chunk = self.client_sock.recv(size - len(msg))
            if not chunk:
                logging.error('action: receive_message | result: fail | error while reading socket')
                return None
            msg += chunk
        
        logging.info(f'action: receive_message | result: success | ip: {self.client_addr[0]} | msg: {msg.rstrip().decode("utf-8")}')

        return msg.rstrip().decode('utf-8')

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