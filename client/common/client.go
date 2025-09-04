package common

import (
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
	protocol *Protocol
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	ctx, cancel := context.WithCancel(context.Background())
	client := &Client{
		config: config,
		ctx:    ctx,
		cancel: cancel,
		protocol: NewProtocol(),
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
func (c *Client) StartClientLoop(bet Bet) {
	// Set up signal handlers for graceful shutdown
	c.setupSignalHandlers()
	
	log.Info("action: client_start | result: success")
	
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Check if shutdown was requested
		select {
		case <-c.ctx.Done():
			log.Info("action: client_loop | result: interrupted")
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

		// Enviar apuesta usando el protocolo
		if err := c.protocol.SendBet(c.conn, bet); err != nil {
			log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			c.closeClientSocket()
			return
		}

		// Recibir respuesta del servidor
		success, dni, numero, err := c.protocol.ReceiveResponse(c.conn)
		c.closeClientSocket()

		if err != nil {
			log.Errorf("action: receive_response | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// Log de confirmación según el formato requerido
		if success {
			log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %s",
				dni,
				numero,
			)
		} else {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %s | numero: %s",
				dni,
				numero,
			)
		}

		// Wait a time between sending one message and the next one
		// Use select to allow interruption during sleep
		select {
		case <-time.After(c.config.LoopPeriod):
			// Sleep completed normally
		case <-c.ctx.Done():
			log.Info("action: client_loop | result: interrupted")
			return
		}
	}
	
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	
	// Crear conexión para notificación y consulta
	if err := c.createClientSocket(); err != nil {
		log.Errorf("action: create_socket_for_notification | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		return
	}
	defer c.closeClientSocket()
	
	// Notificar al servidor que se finalizó el envío de apuestas
	if err := c.protocol.SendFinishedNotification(c.conn, c.config.ID); err != nil {
		log.Errorf("action: send_finished_notification | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		return
	}
	
	// Recibir confirmación de notificación (respuesta simple)
	msgType, _, err := c.protocol.ReceiveMessage(c.conn)
	if err != nil {
		log.Errorf("action: receive_finished_ack | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		return
	}
	
	success := msgType == MSG_SUCCESS
	if success {
		log.Infof("action: finished_notification | result: success | client_id: %v", c.config.ID)
	} else {
		log.Errorf("action: finished_notification | result: fail | client_id: %v", c.config.ID)
		return
	}
	
	// Consultar ganadores de la agencia con retry automático
	ganadores, err := c.queryWinnersWithRetry()
	if err != nil {
		log.Errorf("action: consulta_ganadores | result: fail | client_id: %v | error: %v",
			c.config.ID, err)
		return
	}
	
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d", len(ganadores))
}

// queryWinnersWithRetry consulta los ganadores con reintentos automáticos
func (c *Client) queryWinnersWithRetry() ([]string, error) {
	maxRetries := 10
	retryDelay := time.Second * 2
	
	for attempt := 1; attempt <= maxRetries; attempt++ {
		// Crear nueva conexión para cada intento
		if err := c.createClientSocket(); err != nil {
			log.Errorf("action: create_socket_for_winners | result: fail | client_id: %v | attempt: %d | error: %v",
				c.config.ID, attempt, err)
			return nil, err
		}
		
		// Consultar ganadores
		if err := c.protocol.SendWinnersQuery(c.conn, c.config.ID); err != nil {
			log.Errorf("action: send_winners_query | result: fail | client_id: %v | attempt: %d | error: %v",
				c.config.ID, attempt, err)
			c.closeClientSocket()
			return nil, err
		}
		
		// Recibir respuesta
		msgType, _, err := c.protocol.ReceiveMessage(c.conn)
		if err != nil {
			log.Errorf("action: receive_winners_response | result: fail | client_id: %v | attempt: %d | error: %v",
				c.config.ID, attempt, err)
			c.closeClientSocket()
			return nil, err
		}
		
		c.closeClientSocket()
		
		// Procesar respuesta según el tipo
		switch msgType {
		case MSG_WINNERS_RESPONSE:
			// Recrear conexión para recibir el payload completo
			if err := c.createClientSocket(); err != nil {
				log.Errorf("action: create_socket_for_winners_payload | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				return nil, err
			}
			
			// Enviar consulta nuevamente para recibir el payload
			if err := c.protocol.SendWinnersQuery(c.conn, c.config.ID); err != nil {
				log.Errorf("action: send_winners_query_payload | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				c.closeClientSocket()
				return nil, err
			}
			
			// Recibir respuesta completa
			success, ganadores, err := c.protocol.ReceiveWinnersResponse(c.conn)
			c.closeClientSocket()
			
			if err != nil {
				log.Errorf("action: receive_winners_payload | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				return nil, err
			}
			
			if success {
				log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d | attempts: %d", 
					len(ganadores), attempt)
				return ganadores, nil
			} else {
				log.Errorf("action: consulta_ganadores | result: fail | attempt: %d", attempt)
				return nil, fmt.Errorf("consulta de ganadores falló")
			}
			
		case MSG_RETRY:
			// Recrear conexión para recibir el payload del mensaje de retry
			if err := c.createClientSocket(); err != nil {
				log.Errorf("action: create_socket_for_retry | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				return nil, err
			}
			
			// Enviar consulta nuevamente para recibir el payload
			if err := c.protocol.SendWinnersQuery(c.conn, c.config.ID); err != nil {
				log.Errorf("action: send_winners_query_retry | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				c.closeClientSocket()
				return nil, err
			}
			
			// Recibir mensaje de retry completo
			retryMessage, err := c.protocol.ReceiveRetryResponse(c.conn)
			c.closeClientSocket()
			
			if err != nil {
				log.Errorf("action: receive_retry_message | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				return nil, err
			}
			
			log.Infof("action: retry_message | result: received | client_id: %v | attempt: %d | message: %s",
				c.config.ID, attempt, retryMessage)
			
			// Si no es el último intento, esperar y reintentar
			if attempt < maxRetries {
				log.Infof("action: retry_wait | result: waiting | client_id: %v | attempt: %d/%d | delay: %v",
					c.config.ID, attempt, maxRetries, retryDelay)
				time.Sleep(retryDelay)
				continue
			} else {
				return nil, fmt.Errorf("máximo número de reintentos alcanzado (%d)", maxRetries)
			}
			
		default:
			log.Errorf("action: unknown_message_type | result: fail | client_id: %v | type: %d | attempt: %d",
				c.config.ID, msgType, attempt)
			return nil, fmt.Errorf("tipo de mensaje inesperado: %d", msgType)
		}
	}
	
	return nil, fmt.Errorf("máximo número de reintentos alcanzado")
}

func (c *Client) StartBatchProcessing(bets []Bet, maxBatchSize int) {
	// Set up signal handlers for graceful shutdown
	c.setupSignalHandlers()
	
	log.Info("action: batch_processing_start | result: success")
	
	// Crear conexión TCP
	if err := c.createClientSocket(); err != nil {
		log.Errorf("action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	defer c.closeClientSocket()

	totalBets := len(bets)
	processedBets := 0

	// Procesar apuestas en batches
	for i := 0; i < totalBets; i += maxBatchSize {
		// Check if shutdown was requested
		select {
		case <-c.ctx.Done():
			log.Info("action: batch_processing | result: interrupted")
			return
		default:
			// Continue with normal operation
		}
		
		end := i + maxBatchSize
		if end > totalBets {
			end = totalBets
		}

		batch := bets[i:end]
		batchSize := len(batch)

		// Enviar batch
		err := c.protocol.SendBatch(c.conn, batch)
		if err != nil {
			log.Errorf("action: send_batch | result: fail | client_id: %v | batch: %d-%d | error: %v",
				c.config.ID, i+1, end, err,
			)
			continue
		}

		// Recibir respuesta
		success, _, _, err := c.protocol.ReceiveResponse(c.conn)
		if err != nil {
			log.Errorf("action: receive_batch_response | result: fail | client_id: %v | batch: %d-%d | error: %v",
				c.config.ID, i+1, end, err,
			)
			continue
		}

		if success {
			processedBets += batchSize
			log.Infof("action: batch_processed | result: success | client_id: %v | batch: %d-%d | cantidad: %d",
				c.config.ID, i+1, end, batchSize,
			)
		} else {
			log.Errorf("action: batch_processed | result: fail | client_id: %v | batch: %d-%d | cantidad: %d",
				c.config.ID, i+1, end, batchSize,
			)
		}
	}

	log.Infof("action: batch_processing_complete | result: success | client_id: %v | processed: %d/%d",
		c.config.ID, processedBets, totalBets,
	)
	
	// Cerrar conexión antes de notificar finalización
	c.closeClientSocket()
	
	// Notificar al servidor que se finalizó el envío de apuestas
	if err := c.createClientSocket(); err != nil {
		log.Errorf("action: create_socket_for_notification | result: fail | client_id: %v | error: %v",
			c.config.ID, err)
		return
	}
	
	if err := c.protocol.SendFinishedNotification(c.conn, c.config.ID); err != nil {
		log.Errorf("action: send_finished_notification | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		c.closeClientSocket()
		return
	}
	
	// Recibir confirmación de notificación (respuesta simple)
	msgType, _, err := c.protocol.ReceiveMessage(c.conn)
	if err != nil {
		log.Errorf("action: receive_finished_ack | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		c.closeClientSocket()
		return
	}
	
	success := msgType == MSG_SUCCESS
	if success {
		log.Infof("action: finished_notification | result: success | client_id: %v", c.config.ID)
	} else {
		log.Errorf("action: finished_notification | result: fail | client_id: %v", c.config.ID)
		c.closeClientSocket()
		return
	}
	
	c.closeClientSocket()
	
	// Consultar ganadores de la agencia con retry automático
	ganadores, err := c.queryWinnersWithRetry()
	if err != nil {
		log.Errorf("action: consulta_ganadores | result: fail | client_id: %v | error: %v",
			c.config.ID, err)
		return
	}
	
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d", len(ganadores))
}
