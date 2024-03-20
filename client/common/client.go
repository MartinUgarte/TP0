package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config 	ClientConfig
	conn   	net.Conn
	bet		*Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bet *Bet) *Client {
	client := &Client{
		config: config,
		bet: bet,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// autoincremental msgID to identify every message sent
	// msgID := 1

	sig_ch := make(chan os.Signal, 1)
	signal.Notify(sig_ch, syscall.SIGTERM)

	go func() {
		<- sig_ch
		log.Infof("Signal SIGTERM received")
		c.conn.Close()
		return
	}()

	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()

	// TODO: Modify the send to avoid short-write
	fmt.Fprintf(
		c.conn,
		"[CLIENT %v] Te voy a mandar el bet\n",
		c.config.ID,
	)

	msg, err := bufio.NewReader(c.conn).ReadString('\n')
	
	c.conn.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		c.config.ID,
		msg,
	)
}
