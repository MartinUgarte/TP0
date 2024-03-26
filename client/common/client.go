package common

import (
	"net"
	"time"
	"os"
	"fmt"
	"os/signal"
	"syscall"
	"strings"
	"bufio"
	log "github.com/sirupsen/logrus"
)

const (
	BETS_PER_BATCH = 160 // less than 8kB per batch 
	HEADER_SEPARATOR = "#"
	BET_SEPARATOR = "\t"
	FLAG_SEPARATOR = ","
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
	log.Infof("action: connected to server | result: success")
	return nil
}

func (c *Client) startSignalHandler(sigterm chan bool) {
	sig_ch := make(chan os.Signal, 1)
	signal.Notify(sig_ch, syscall.SIGTERM)

	go func() {
		<- sig_ch
		log.Infof("action: sigterm_received | client_id: %v", c.config.ID)
		c.conn.Close()
		sigterm <- true
	}()
}

func (c *Client) sendBetsToServer(bets []string, end bool) bool {
	concatenated_bets := strings.Join(bets, BET_SEPARATOR)
	header := len(concatenated_bets)
	endflag := 0
	if end { endflag = 1 }
	message := fmt.Sprintf("%d%s%d%s%s", header, FLAG_SEPARATOR, endflag, HEADER_SEPARATOR, concatenated_bets)

	if !SendMessageToServer(message, c) {
		return false
	}

	_, err := ReceiveServerMessage(c)

	if err != nil {
		return false
	}

	return true
}

// Reads bets from the agency file and sends them to the server using chunks
func (c *Client) readBetsFromFile(filename string, sigterm chan bool) bool {

	// Open the file
	file, err := os.Open(filename)
	if err != nil {
		log.Infof("action: open_file | result: fail | client_id: %v | error: %v", c.config)
		file.Close()
		return false
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	bets := []string{}

	// Read the file line by line
	for scanner.Scan() {
		line := scanner.Text()
		bet := c.config.ID + "," + line
		bets = append(bets, bet)

		if len(bets) < BETS_PER_BATCH {
			continue
		}
		
		if !c.sendBetsToServer(bets, false) {
			return false
		}
	
		bets = []string{}
	}

	if !c.sendBetsToServer(bets, true) {
		return false
	}

	return true
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	sigterm := make(chan bool, 1)

	// Start signal handler
	c.startSignalHandler(sigterm)

	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()

	filename := fmt.Sprintf("agency-%s.csv", c.config.ID)

	if !c.readBetsFromFile(filename, sigterm) {
		c.conn.Close()
		return
	}

	log.Infof("action: send_bets | result: success | client_id: %v", c.config.ID)
	
	c.conn.Close()

}
