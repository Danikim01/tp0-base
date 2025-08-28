package common

import (
	"encoding/binary"
	"fmt"
	"net"
)

// Constantes del protocolo
const (
	DELIMITER        = 0xFF
	HEADER_SIZE      = 5 // 4 bytes longitud + 1 byte tipo
	MAX_MESSAGE_SIZE = 8192 // 8KB máximo
)

// Tipos de mensaje
const (
	MSG_BET             = 0x01
	MSG_BATCH           = 0x02
	MSG_SUCCESS         = 0x03
	MSG_ERROR           = 0x04
	MSG_FINISHED        = 0x05
	MSG_WINNERS_QUERY   = 0x06
	MSG_WINNERS_RESPONSE = 0x07
)

// Bet representa una apuesta de quiniela
type Bet struct {
	Agency     string
	Nombre     string
	Apellido   string
	DNI        string
	Nacimiento string
	Numero     string
}

// Protocol maneja la comunicación entre cliente y servidor
type Protocol struct{}

// NewProtocol crea una nueva instancia del protocolo
func NewProtocol() *Protocol {
	return &Protocol{}
}

// readExact lee exactamente 'size' bytes del socket
func (p *Protocol) readExact(conn net.Conn, size int) ([]byte, error) {
	data := make([]byte, size)
	totalRead := 0
	
	for totalRead < size {
		n, err := conn.Read(data[totalRead:])
		if err != nil {
			return nil, fmt.Errorf("error leyendo datos: %v", err)
		}
		if n == 0 {
			return nil, fmt.Errorf("conexión cerrada por el servidor")
		}
		totalRead += n
	}
	
	return data, nil
}

// writeExact escribe exactamente todos los datos al socket
func (p *Protocol) writeExact(conn net.Conn, data []byte) error {
	totalSent := 0
	
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			return fmt.Errorf("error escribiendo datos: %v", err)
		}
		if n == 0 {
			return fmt.Errorf("conexión rota")
		}
		totalSent += n
	}
	
	return nil
}

// encodeString codifica una string con su longitud
func (p *Protocol) encodeString(s string) []byte {
	encoded := []byte(s)
	length := uint16(len(encoded))
	
	result := make([]byte, 2+len(encoded))
	binary.BigEndian.PutUint16(result[0:2], length)
	copy(result[2:], encoded)
	
	return result
}

// decodeString decodifica una string con su longitud
func (p *Protocol) decodeString(data []byte, offset int) (string, int, error) {
	if offset+2 > len(data) {
		return "", offset, fmt.Errorf("datos insuficientes para decodificar string")
	}
	
	length := binary.BigEndian.Uint16(data[offset : offset+2])
	offset += 2
	
	if offset+int(length) > len(data) {
		return "", offset, fmt.Errorf("datos insuficientes para decodificar string")
	}
	
	stringData := data[offset : offset+int(length)]
	return string(stringData), offset + int(length), nil
}

// SendMessage envía un mensaje completo al servidor
func (p *Protocol) SendMessage(conn net.Conn, msgType byte, payload []byte) error {
	// Construir mensaje completo
	header := make([]byte, HEADER_SIZE)
	binary.BigEndian.PutUint32(header[0:4], uint32(len(payload)))
	header[4] = msgType
	
	message := append(header, payload...)
	message = append(message, DELIMITER)
	
	// Enviar mensaje completo
	return p.writeExact(conn, message)
}

// ReceiveMessage recibe un mensaje completo del servidor
func (p *Protocol) ReceiveMessage(conn net.Conn) (byte, []byte, error) {
	// Leer header (longitud + tipo)
	header, err := p.readExact(conn, HEADER_SIZE)
	if err != nil {
		return 0, nil, fmt.Errorf("error leyendo header: %v", err)
	}
	
	// Parsear header
	payloadLength := binary.BigEndian.Uint32(header[0:4])
	msgType := header[4]
	
	// Validar longitud
	if payloadLength > MAX_MESSAGE_SIZE {
		return 0, nil, fmt.Errorf("mensaje demasiado grande (%d bytes)", payloadLength)
	}
	
	// Leer payload
	payload, err := p.readExact(conn, int(payloadLength))
	if err != nil {
		return 0, nil, fmt.Errorf("error leyendo payload: %v", err)
	}
	
	// Leer delimitador
	delimiter, err := p.readExact(conn, 1)
	if err != nil {
		return 0, nil, fmt.Errorf("error leyendo delimitador: %v", err)
	}
	
	if delimiter[0] != DELIMITER {
		return 0, nil, fmt.Errorf("delimitador inválido")
	}
	
	return msgType, payload, nil
}

// EncodeBet codifica una apuesta a bytes
func (p *Protocol) EncodeBet(bet Bet) []byte {
	payload := make([]byte, 0)
	payload = append(payload, p.encodeString(bet.Agency)...)
	payload = append(payload, p.encodeString(bet.Nombre)...)
	payload = append(payload, p.encodeString(bet.Apellido)...)
	payload = append(payload, p.encodeString(bet.DNI)...)
	payload = append(payload, p.encodeString(bet.Nacimiento)...)
	payload = append(payload, p.encodeString(bet.Numero)...)
	return payload
}

// DecodeBet decodifica una apuesta desde el payload
func (p *Protocol) DecodeBet(payload []byte) (Bet, error) {
	var bet Bet
	offset := 0
	
	// Decodificar campos
	agency, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando agency: %v", err)
	}
	
	nombre, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando nombre: %v", err)
	}
	
	apellido, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando apellido: %v", err)
	}
	
	dni, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando DNI: %v", err)
	}
	
	nacimiento, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando nacimiento: %v", err)
	}
	
	numero, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return bet, fmt.Errorf("error decodificando numero: %v", err)
	}
	
	bet = Bet{
		Agency:     agency,
		Nombre:     nombre,
		Apellido:   apellido,
		DNI:        dni,
		Nacimiento: nacimiento,
		Numero:     numero,
	}
	
	return bet, nil
}

// SendBet envía una apuesta al servidor
func (p *Protocol) SendBet(conn net.Conn, bet Bet) error {
	payload := p.EncodeBet(bet)
	return p.SendMessage(conn, MSG_BET, payload)
}

// EncodeBatch codifica un batch de apuestas a bytes
func (p *Protocol) EncodeBatch(bets []Bet) []byte {
	payload := make([]byte, 0)
	
	// Escribir cantidad de apuestas (4 bytes)
	cantidad := uint32(len(bets))
	cantidadBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(cantidadBytes, cantidad)
	payload = append(payload, cantidadBytes...)
	
	// Escribir cada apuesta con su longitud
	for _, bet := range bets {
		betData := p.EncodeBet(bet)
		betLength := uint32(len(betData))
		betLengthBytes := make([]byte, 4)
		binary.BigEndian.PutUint32(betLengthBytes, betLength)
		payload = append(payload, betLengthBytes...)
		payload = append(payload, betData...)
	}
	
	return payload
}

// SendBatch envía un batch de apuestas al servidor
func (p *Protocol) SendBatch(conn net.Conn, bets []Bet) error {
	payload := p.EncodeBatch(bets)
	return p.SendMessage(conn, MSG_BATCH, payload)
}

// SendFinishedNotification envía notificación de finalización al servidor
func (p *Protocol) SendFinishedNotification(conn net.Conn, agencyID string) error {
	payload := p.encodeString(agencyID)
	return p.SendMessage(conn, MSG_FINISHED, payload)
}

// SendWinnersQuery envía consulta de ganadores al servidor
func (p *Protocol) SendWinnersQuery(conn net.Conn, agencyID string) error {
	payload := p.encodeString(agencyID)
	return p.SendMessage(conn, MSG_WINNERS_QUERY, payload)
}

// ReceiveWinnersResponse recibe la respuesta con los ganadores del servidor
func (p *Protocol) ReceiveWinnersResponse(conn net.Conn) (bool, []string, error) {
	msgType, payload, err := p.ReceiveMessage(conn)
	if err != nil {
		return false, nil, fmt.Errorf("error recibiendo respuesta de ganadores: %v", err)
	}
	
	if msgType != MSG_WINNERS_RESPONSE {
		return false, nil, fmt.Errorf("tipo de mensaje inesperado: %d", msgType)
	}
	
	// Decodificar respuesta de ganadores
	offset := 0
	
	// Leer cantidad de ganadores (4 bytes)
	if offset+4 > len(payload) {
		return false, nil, fmt.Errorf("datos insuficientes para decodificar cantidad de ganadores")
	}
	cantidad := binary.BigEndian.Uint32(payload[offset : offset+4])
	offset += 4
	
	// Leer cada DNI ganador
	ganadores := make([]string, 0, cantidad)
	for i := uint32(0); i < cantidad; i++ {
		dni, newOffset, err := p.decodeString(payload, offset)
		if err != nil {
			return false, nil, fmt.Errorf("error decodificando DNI ganador %d: %v", i+1, err)
		}
		ganadores = append(ganadores, dni)
		offset = newOffset
	}
	
	return true, ganadores, nil
}

// ReceiveResponse recibe la respuesta del servidor
func (p *Protocol) ReceiveResponse(conn net.Conn) (bool, string, string, error) {
	msgType, payload, err := p.ReceiveMessage(conn)
	if err != nil {
		return false, "", "", fmt.Errorf("error recibiendo respuesta: %v", err)
	}
	
	if msgType != MSG_SUCCESS && msgType != MSG_ERROR {
		return false, "", "", fmt.Errorf("tipo de mensaje inesperado: %d", msgType)
	}
	
	// Decodificar respuesta
	offset := 0
	dni, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return false, "", "", fmt.Errorf("error decodificando DNI en respuesta: %v", err)
	}
	
	numero, offset, err := p.decodeString(payload, offset)
	if err != nil {
		return false, "", "", fmt.Errorf("error decodificando numero en respuesta: %v", err)
	}
	
	success := msgType == MSG_SUCCESS
	return success, dni, numero, nil
}
