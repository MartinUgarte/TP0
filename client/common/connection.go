package common

import (
	"fmt"
	"strings"
	"strconv"
	log "github.com/sirupsen/logrus"
)

func SendMessageToServer(message string, c *Client) bool {
	totalSent := 0

	for totalSent < len(message) {
		sent, err := fmt.Fprintf(c.conn, message[totalSent:])
		if err != nil || sent == 0 {
			log.Infof("action: send_message | result: fail | client_id: %v | error while sending message",
			c.config.ID,
			)
			return false
		}
		totalSent += sent	
	}
	return true
}

func ReceiveServerMessage(c *Client) (string, error) {
	size, err := readHeader(c)
	if err != nil {
		log.Infof("action: receive_header | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return "", err
	}

	chunk := make([]byte, size + 1) // includes the \n
	_, err_r := c.conn.Read(chunk)

	if err_r != nil {
		log.Infof("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err_r,
		)
		return "", err_r
	}

	return avoidShortRead(c, chunk, size)
}

func readHeader(c *Client) (int, error){
	header := ""

	for {
		read := make([]byte, 1)
		_, err := c.conn.Read(read)
		if err != nil {
			return 0, err
		}
		if string(read) == HEADER_SEPARATOR {
			break
		}

		header += string(read)
	}
	size, err := strconv.Atoi(header)

	if err != nil {
		log.Infof("action: convert_header_to_int | result: fail | e: %v", err)
		return 0, err
	}

	return size, nil
}

func avoidShortRead(c *Client, message []byte, size int) (string, error) {
	msg_bytes := message

	for len(msg_bytes) < size {
		chunk := make([]byte, size - len(msg_bytes))
        n, err := c.conn.Read(chunk)
		if err != nil {
			log.Infof("action: read message | result: fail | error while reading chunk")
			return "", nil
		}
		msg_bytes = append(msg_bytes, chunk[:n]...)
	}

	return strings.TrimSpace(string(msg_bytes)), nil
}