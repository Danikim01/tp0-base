package common

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net"
)

// Bet representa una apuesta de quiniela
type Bet struct {
	Nombre    string `json:"nombre"`
	Apellido  string `json:"apellido"`
	DNI       string `json:"dni"`
	Nacimiento string `json:"nacimiento"`
	Numero    string `json:"numero"`
}

// BetRequest representa el mensaje de solicitud de apuesta
type BetRequest struct {
	Type string `json:"type"`
	Bet  Bet    `json:"bet"`
}

// BetResponse representa la respuesta del servidor
type BetResponse struct {
	Type   string `json:"type"`
	Status string `json:"status"`
	DNI    string `json:"dni"`
	Numero string `json:"numero"`
}

// Protocol maneja la comunicación entre cliente y servidor
type Protocol struct{}

// NewProtocol crea una nueva instancia del protocolo
func NewProtocol() *Protocol {
	return &Protocol{}
}

// SendBet envía una apuesta al servidor evitando short-write
func (p *Protocol) SendBet(conn net.Conn, bet Bet) error {
	request := BetRequest{
		Type: "bet",
		Bet:  bet,
	}
	
	data, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("error serializando apuesta: %v", err)
	}
	
	// Agregar delimitador de mensaje
	message := append(data, '\n')
	
	// Enviar datos completos evitando short-write
	return p.sendComplete(conn, message)
}

// sendComplete envía todos los datos evitando short-write
func (p *Protocol) sendComplete(conn net.Conn, data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			return fmt.Errorf("error escribiendo datos: %v", err)
		}
		totalSent += n
	}
	return nil
}

// ReceiveResponse recibe la respuesta del servidor evitando short-read
func (p *Protocol) ReceiveResponse(conn net.Conn) (*BetResponse, error) {
	reader := bufio.NewReader(conn)
	
	// Leer hasta el delimitador de línea
	line, err := reader.ReadString('\n')
	if err != nil {
		if err == io.EOF {
			return nil, fmt.Errorf("conexión cerrada por el servidor")
		}
		return nil, fmt.Errorf("error leyendo respuesta: %v", err)
	}
	
	// Parsear la respuesta JSON
	var response BetResponse
	if err := json.Unmarshal([]byte(line), &response); err != nil {
		return nil, fmt.Errorf("error parseando respuesta: %v", err)
	}
	
	return &response, nil
}
