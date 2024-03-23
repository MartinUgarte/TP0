package common

import (
	"bufio"
	"fmt"
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
	msg, err := bufio.NewReader(c.conn).ReadString('\n')
	
	if err != nil {
		log.Infof("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return "", err
	}

	return msg, nil
}