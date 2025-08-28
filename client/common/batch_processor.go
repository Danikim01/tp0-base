package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"net"
	"os"
	"strings"
)

// BatchProcessor maneja el procesamiento de batches de apuestas
type BatchProcessor struct {
	protocol *Protocol
	maxBatchSize int
}

// NewBatchProcessor crea un nuevo procesador de batches
func NewBatchProcessor(protocol *Protocol, maxBatchSize int) *BatchProcessor {
	return &BatchProcessor{
		protocol: protocol,
		maxBatchSize: maxBatchSize,
	}
}

// BetFromCSV representa una apuesta leída desde CSV
type BetFromCSV struct {
	Agency     string
	FirstName  string
	LastName   string
	Document   string
	Birthdate  string
	Number     string
}

// ReadBetsFromCSV lee apuestas desde un archivo CSV
func (bp *BatchProcessor) ReadBetsFromCSV(filename string) ([]Bet, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("error abriendo archivo %s: %v", filename, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	
	// No hay header en el CSV, empezamos directamente con los datos

	var bets []Bet
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("error leyendo registro: %v", err)
		}

		// Parsear registro CSV (formato: nombre,apellido,documento,nacimiento,numero)
		if len(record) < 5 {
			continue // Saltar registros incompletos
		}

		bet := Bet{
			Nombre:     strings.TrimSpace(record[0]),
			Apellido:   strings.TrimSpace(record[1]),
			DNI:        strings.TrimSpace(record[2]),
			Nacimiento: strings.TrimSpace(record[3]),
			Numero:     strings.TrimSpace(record[4]),
		}

		// Validar que los campos no estén vacíos
		if bet.Nombre == "" || bet.Apellido == "" || bet.DNI == "" || bet.Nacimiento == "" || bet.Numero == "" {
			continue // Saltar registros con campos vacíos
		}

		bets = append(bets, bet)
	}

	return bets, nil
}

// ProcessBetsInBatches procesa las apuestas en batches y las envía al servidor
func (bp *BatchProcessor) ProcessBetsInBatches(conn net.Conn, bets []Bet) error {
	totalBets := len(bets)
	processedBets := 0

	for i := 0; i < totalBets; i += bp.maxBatchSize {
		end := i + bp.maxBatchSize
		if end > totalBets {
			end = totalBets
		}

		batch := bets[i:end]
		batchSize := len(batch)

		// Enviar batch
		err := bp.protocol.SendBatch(conn, batch)
		if err != nil {
			return fmt.Errorf("error enviando batch %d-%d: %v", i+1, end, err)
		}

		// Recibir respuesta
		success, _, _, err := bp.protocol.ReceiveResponse(conn)
		if err != nil {
			return fmt.Errorf("error recibiendo respuesta del batch %d-%d: %v", i+1, end, err)
		}

		if success {
			processedBets += batchSize
			fmt.Printf("Batch %d-%d procesado exitosamente (%d apuestas)\n", i+1, end, batchSize)
		} else {
			fmt.Printf("Error procesando batch %d-%d (%d apuestas)\n", i+1, end, batchSize)
		}
	}

	fmt.Printf("Procesamiento completado: %d/%d apuestas procesadas\n", processedBets, totalBets)
	return nil
}

// GetAgencyFilename genera el nombre del archivo para una agencia específica
func GetAgencyFilename(agencyID int) string {
	// En Docker Compose, el directorio .data se monta en /data
	// Verificar si estamos en Docker (existe /data) o en local (.data)
	if _, err := os.Stat("/data"); err == nil {
		// Estamos en Docker, usar /data
		return fmt.Sprintf("/data/agency-%d.csv", agencyID)
	} else {
		// Estamos en local, usar .data
		return fmt.Sprintf(".data/agency-%d.csv", agencyID)
	}
}
