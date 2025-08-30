package common

import (
	"bufio"
	"context"
	"fmt"
	"net"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	mu     sync.Mutex
	ctx    context.Context
	cancel context.CancelFunc
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	ctx, cancel := context.WithCancel(context.Background())
	client := &Client{
		config: config,
		ctx:    ctx,
		cancel: cancel,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

// closeClientSocket Closes the client socket gracefully
func (c *Client) closeClientSocket() {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	if c.conn != nil {
		log.Info("action: close_client_socket | result: in_progress")
		c.conn.Close()
		c.conn = nil
		log.Info("action: close_client_socket | result: success")
	}
}

// gracefulShutdown Performs graceful shutdown of all resources
func (c *Client) gracefulShutdown() {
	log.Info("action: graceful_shutdown | result: in_progress")
	
	// Cancel context to stop any ongoing operations
	c.cancel()
	
	// Close client socket
	c.closeClientSocket()
	
	log.Info("action: graceful_shutdown | result: success")
}

// setupSignalHandlers Sets up signal handlers for graceful shutdown
func (c *Client) setupSignalHandlers() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM, syscall.SIGINT)
	
	go func() {
		sig := <-sigChan
		log.Infof("action: signal_received | result: success | signal: %v", sig)
		c.gracefulShutdown()
		os.Exit(0)
	}()
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// Set up signal handlers for graceful shutdown
	c.setupSignalHandlers()
	
	log.Info("action: client_start | result: success")
	
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Check if shutdown was requested
		select {
		case <-c.ctx.Done():
			log.Info("action: client_loop | result: success")
			return
		default:
			// Continue with normal operation
		}
		
		// Create the connection the server in every loop iteration. Send an
		if err := c.createClientSocket(); err != nil {
			log.Errorf("action: create_socket | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// TODO: Modify the send to avoid short-write
		fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		c.closeClientSocket()

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

		// Wait a time between sending one message and the next one
		// Use select to allow interruption during sleep
		select {
		case <-time.After(c.config.LoopPeriod):
			// Sleep completed normally
		case <-c.ctx.Done():
			log.Info("action: client_loop | result: success")
			return
		}
	}
	
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
