# Protocolo de Comunicación Propio - TP0


## Estructura del Protocolo

**Formato de Mensaje:**
```
[LONGITUD][TIPO][PAYLOAD][DELIMITADOR]
```

Donde:
- `[LONGITUD]`: 4 bytes (uint32) en big-endian indicando la longitud del payload
- `[TIPO]`: 1 byte indicando el tipo de mensaje
- `[PAYLOAD]`: Datos del mensaje (longitud variable)
- `[DELIMITADOR]`: 1 byte con valor `0xFF`

**Tipos de Mensaje:**
- `0x01`: Apuesta individual
- `0x02`: Batch de apuestas
- `0x03`: Respuesta de éxito
- `0x04`: Respuesta de error

## Formato del Payload

**Apuesta Individual (Tipo 0x01):**
```
[NOMBRE_LEN][NOMBRE][APELLIDO_LEN][APELLIDO][DNI_LEN][DNI][NACIMIENTO_LEN][NACIMIENTO][NUMERO_LEN][NUMERO]
```

**Batch de Apuestas (Tipo 0x02):**
```
[CANTIDAD_APUESTAS][LONGITUD_APUESTA_1][APUESTA_1][LONGITUD_APUESTA_2][APUESTA_2]...[LONGITUD_APUESTA_N][APUESTA_N]
```

Donde:
- `[CANTIDAD_APUESTAS]`: 4 bytes (uint32) en big-endian indicando el número de apuestas
- `[LONGITUD_APUESTA_X]`: 4 bytes (uint32) en big-endian indicando la longitud de cada apuesta
- `[APUESTA_X]`: Datos de la apuesta individual en formato estándar

**Respuesta (Tipos 0x03, 0x04):**
```
[DNI_LEN][DNI][NUMERO_LEN][NUMERO]
```

## Implementación del Protocolo

### Constantes del Protocolo

```python
# Python
DELIMITER = b'\xFF'
HEADER_SIZE = 5  # 4 bytes longitud + 1 byte tipo
MAX_MESSAGE_SIZE = 8192  # 8KB máximo
```

```go
// Go
const (
    DELIMITER        = 0xFF
    HEADER_SIZE      = 5 // 4 bytes longitud + 1 byte tipo
    MAX_MESSAGE_SIZE = 8192 // 8KB máximo
)
```

### Funciones Principales

#### Envío de Mensajes
```python
def send_message(client_sock, msg_type, payload):
    header = struct.pack('!IB', len(payload), msg_type)
    message = header + payload + DELIMITER
    return write_exact(client_sock, message)
```

```go
func (p *Protocol) SendMessage(conn net.Conn, msgType byte, payload []byte) error {
    header := make([]byte, HEADER_SIZE)
    binary.BigEndian.PutUint32(header[0:4], uint32(len(payload)))
    header[4] = msgType
    
    message := append(header, payload...)
    message = append(message, DELIMITER)
    
    return p.writeExact(conn, message)
}
```

#### Envío de Batches
```python
def encode_batch(bets):
    payload = b""
    # Escribir cantidad de apuestas
    payload += struct.pack('!I', len(bets))
    
    # Escribir cada apuesta con su longitud
    for bet in bets:
        bet_data = encode_bet(bet)
        payload += struct.pack('!I', len(bet_data))
        payload += bet_data
    
    return payload
```

```go
func (p *Protocol) EncodeBatch(bets []Bet) []byte {
    payload := make([]byte, 0)
    
    // Escribir cantidad de apuestas
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
```

#### Recepción de Mensajes
```python
def receive_message(client_sock):
    header = read_exact(client_sock, HEADER_SIZE)
    payload_length, msg_type = struct.unpack('!IB', header)
    payload = read_exact(client_sock, payload_length)
    delimiter = read_exact(client_sock, 1)
    return msg_type, payload
```

```go
func (p *Protocol) ReceiveMessage(conn net.Conn) (byte, []byte, error) {
    header, err := p.readExact(conn, HEADER_SIZE)
    payloadLength := binary.BigEndian.Uint32(header[0:4])
    msgType := header[4]
    
    payload, err := p.readExact(conn, int(payloadLength))
    delimiter, err := p.readExact(conn, 1)
    
    return msgType, payload, nil
}
```

#### Decodificación de Batches
```python
def decode_batch(payload):
    offset = 0
    
    # Leer cantidad de apuestas
    cantidad = struct.unpack('!I', payload[offset:offset+4])[0]
    offset += 4
    
    bets = []
    for _ in range(cantidad):
        # Leer longitud de la apuesta
        bet_length = struct.unpack('!I', payload[offset:offset+4])[0]
        offset += 4
        
        # Leer apuesta
        bet_data = payload[offset:offset+bet_length]
        bet = decode_bet(bet_data)
        bets.append(bet)
        offset += bet_length
    
    return bets
```

```go
func (p *Protocol) DecodeBatch(payload []byte) ([]Bet, error) {
    offset := 0
    
    // Leer cantidad de apuestas
    cantidad := binary.BigEndian.Uint32(payload[offset:offset+4])
    offset += 4
    
    bets := make([]Bet, 0, cantidad)
    for i := uint32(0); i < cantidad; i++ {
        // Leer longitud de la apuesta
        betLength := binary.BigEndian.Uint32(payload[offset:offset+4])
        offset += 4
        
        // Leer apuesta
        betData := payload[offset:offset+betLength]
        bet, err := p.DecodeBet(betData)
        if err != nil {
            return nil, err
        }
        bets = append(bets, bet)
        offset += betLength
    }
    
    return bets, nil
}
```

## Manejo de Errores

### Validaciones Implementadas
1. **Longitud de mensaje**: Máximo 8KB para evitar ataques DoS
2. **Delimitador**: Verificación del byte delimitador
3. **Datos completos**: Lectura/escritura exacta de bytes
4. **Tipos de mensaje**: Validación de tipos válidos
5. **Strings**: Verificación de longitud y codificación UTF-8

### Códigos de Error
- Conexión cerrada inesperadamente
- Mensaje demasiado grande
- Delimitador inválido
- Payload incompleto
- Tipo de mensaje desconocido
- Error de codificación/decodificación

## Ejemplo de Uso

### Cliente (Go) - Apuesta Individual
```go
protocol := NewProtocol()
bet := Bet{Nombre: "Juan", Apellido: "Pérez", DNI: "12345678", ...}

// Enviar apuesta individual
err := protocol.SendBet(conn, bet)

// Recibir respuesta
success, dni, numero, err := protocol.ReceiveResponse(conn)
```

### Cliente (Go) - Procesamiento por Batches
```go
protocol := NewProtocol()
batchProcessor := NewBatchProcessor(protocol, maxBatchSize)

// Leer apuestas desde CSV
bets, err := batchProcessor.ReadBetsFromCSV("/data/agency-1.csv")

// Procesar en batches
for i := 0; i < len(bets); i += maxBatchSize {
    end := min(i+maxBatchSize, len(bets))
    batch := bets[i:end]
    
    // Enviar batch
    err := protocol.SendBatch(conn, batch)
    
    // Recibir respuesta
    success, _, _, err := protocol.ReceiveResponse(conn)
}
```

### Servidor (Python) - Procesamiento Mixto
```python
protocol = Protocol()

# Procesar mensaje (apuesta individual o batch)
success = protocol.process_message(client_sock)

# El servidor detecta automáticamente el tipo de mensaje:
# - MSG_BET (0x01): Procesa apuesta individual
# - MSG_BATCH (0x02): Procesa batch de apuestas
```

### Servidor (Python) - Procesamiento de Batch
```python
# Recibir batch
bets = protocol.receive_batch(client_sock)

# Procesar todas las apuestas
success = True
for bet in bets:
    try:
        store_bet(bet)
        logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document}")
    except Exception as e:
        success = False
        break

# Log del resultado del batch
if success:
    logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
else:
    logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")

# Enviar respuesta
protocol.send_response(client_sock, success, bets[0].document, str(bets[0].number))
```

## Configuración

El protocolo está configurado para:
- **Puerto**: 12345 (configurable)
- **Tamaño máximo**: 8KB por mensaje
- **Timeout**: Sin timeout específico (usa configuración del socket)
- **Codificación**: UTF-8 para strings

### Configuración de Batches

```yaml
batch:
  maxAmount: 50  # Máximo 50 apuestas por batch (ajustado para < 8KB)
```

### Estructura de Archivos CSV

```
.data/
├── agency-1.csv    # Apuestas de la agencia 1
├── agency-2.csv    # Apuestas de la agencia 2
└── agency-N.csv    # Apuestas de la agencia N
```

**Formato CSV:**
```csv
agency,first_name,last_name,document,birthdate,number
1,Juan,Pérez,12345678,1990-01-01,1234
1,María,González,23456789,1985-05-15,5678
```

## Logs del Protocolo

El protocolo genera logs detallados para debugging:

### Logs de Apuestas Individuales
- Recepción/envío de mensajes
- Errores de validación
- Problemas de conexión
- Confirmaciones de operaciones

### Logs de Batches

**Cliente:**
```
action: batch_processing_start | result: success
action: batch_processed | result: success | client_id: 1 | batch: 1-10 | cantidad: 10
action: batch_processing_complete | result: success | client_id: 1 | processed: 10/10
```

**Servidor:**
```
action: apuesta_almacenada | result: success | dni: 12345678 | numero: 1234
action: apuesta_almacenada | result: success | dni: 23456789 | numero: 5678
...
action: apuesta_recibida | result: success | cantidad: 10
```

### Logs de Error en Batches
```
action: apuesta_recibida | result: fail | cantidad: 10
action: batch_processed | result: fail | client_id: 1 | batch: 1-10 | cantidad: 10
```

### Implementación de Batches

#### Estructura del Batch
```
[CANTIDAD][LEN_APUESTA_1][APUESTA_1][LEN_APUESTA_2][APUESTA_2]...[LEN_APUESTA_N][APUESTA_N]
```

#### Flujo de Procesamiento
1. **Cliente**: Lee apuestas desde archivo CSV
2. **Cliente**: Agrupa apuestas en batches según `maxAmount`
3. **Cliente**: Envía batch completo al servidor
4. **Servidor**: Recibe y decodifica el batch
5. **Servidor**: Procesa cada apuesta individualmente
6. **Servidor**: Responde con éxito solo si todas las apuestas se procesaron correctamente
7. **Cliente**: Recibe confirmación del batch completo

#### Manejo de Errores en Batches
- Si una apuesta falla, todo el batch se marca como fallido
- El servidor responde con `MSG_ERROR` para batches fallidos
- Los logs indican la cantidad total de apuestas procesadas
- Se mantiene la atomicidad del batch

### Configuración de Volúmenes Docker

```yaml
volumes:
  - ./.data:/data:ro  # Montaje de archivos CSV
```

Los archivos CSV se montan como volúmenes de solo lectura para:
- Persistencia de datos fuera de las imágenes
- Fácil actualización de datos sin reconstruir imágenes
- Separación de datos de la lógica de aplicación


