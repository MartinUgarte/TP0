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

const (
	SIZE_SEPARATOR = " "
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
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
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

func (c *Client) startSignalHandler(done chan bool) {
	sig_ch := make(chan os.Signal, 1)
	signal.Notify(sig_ch, syscall.SIGTERM)

	go func() {
		<- sig_ch
		c.conn.Close()
		done <- true
	}()
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(bet *Bet) {

	// Start signal handler
	done := make(chan bool, 1)
	c.startSignalHandler(done)

	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()

	bet_info := bet.Serialize()
	
	message := fmt.Sprintf("%d%s%s", len(bet_info), SIZE_SEPARATOR, bet_info)

	fmt.Fprintf(
		c.conn,
		message,
	)

	log.Infof("action: send_message | result: success | client_id: %v | msg: %v",
		c.config.ID,
		message,
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
		msg[:len(msg)-1],
	)
}
