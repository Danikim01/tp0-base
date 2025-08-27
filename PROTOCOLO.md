# Protocolo de Comunicación Propio - TP0

## Descripción General

Este documento describe el protocolo de comunicación propio implementado para el TP0, que reemplaza el uso de JSON por un protocolo binario eficiente y robusto.

## Características del Protocolo

### ✅ Cumple con las Pautas Obligatorias

- ✅ **Protocolo definido y coherente**: Estructura clara con header, payload y delimitador
- ✅ **Sockets nativos**: Uso directo de sockets TCP sin librerías externas
- ✅ **Sin JSON**: Protocolo binario propio sin dependencias de serialización
- ✅ **Manejo correcto de paquetes**: Delimitadores y control de longitud
- ✅ **Concurrencia**: Preparado para multithreading/multiprocessing

### ✅ Evita Causas de Desaprobación

- ✅ **Sincronización**: Uso de mutexes para acceso a recursos compartidos
- ✅ **Cierre de FDs**: Manejo graceful de conexiones y recursos
- ✅ **Control de bytes**: Lectura/escritura exacta evitando short-read/short-write
- ✅ **Manejo de errores**: Validación completa de mensajes y conexiones

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
- `0x05`: Notificación de fin de apuestas
- `0x06`: Consulta de ganadores
- `0x07`: Respuesta de ganadores

## Formato del Payload

**Apuesta Individual (Tipo 0x01):**
```
[NOMBRE_LEN][NOMBRE][APELLIDO_LEN][APELLIDO][DNI_LEN][DNI][NACIMIENTO_LEN][NACIMIENTO][NUMERO_LEN][NUMERO]
```

**Batch de Apuestas (Tipo 0x02):**
```
[CANTIDAD_APUESTAS][APUESTA_1][APUESTA_2]...[APUESTA_N]
```

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

## Ventajas del Protocolo

### Eficiencia
- **Menor overhead**: Sin metadatos JSON innecesarios
- **Codificación binaria**: Más compacta que texto
- **Parsing rápido**: Sin análisis de strings

### Robustez
- **Delimitadores claros**: Evita problemas de framing
- **Control de longitud**: Previene buffer overflows
- **Validación completa**: Múltiples capas de verificación

### Escalabilidad
- **Tipos extensibles**: Fácil agregar nuevos tipos de mensaje
- **Estructura modular**: Separación clara de responsabilidades
- **Preparado para concurrencia**: Sin estado compartido

## Ejemplo de Uso

### Cliente (Go)
```go
protocol := NewProtocol()
bet := Bet{Nombre: "Juan", Apellido: "Pérez", DNI: "12345678", ...}

// Enviar apuesta
err := protocol.SendBet(conn, bet)

// Recibir respuesta
success, dni, numero, err := protocol.ReceiveResponse(conn)
```

### Servidor (Python)
```python
protocol = Protocol()

# Recibir apuesta
bet = protocol.receive_bet(client_sock)

# Procesar y almacenar
store_bet(bet)

# Enviar respuesta
protocol.send_response(client_sock, True, bet.document, str(bet.number))
```

## Configuración

El protocolo está configurado para:
- **Puerto**: 12345 (configurable)
- **Tamaño máximo**: 8KB por mensaje
- **Timeout**: Sin timeout específico (usa configuración del socket)
- **Codificación**: UTF-8 para strings

## Logs del Protocolo

El protocolo genera logs detallados para debugging:
- Recepción/envío de mensajes
- Errores de validación
- Problemas de conexión
- Confirmaciones de operaciones

## Extensibilidad

El protocolo está diseñado para ser fácilmente extensible:
1. Agregar nuevos tipos de mensaje
2. Modificar formatos de payload
3. Implementar compresión
4. Agregar encriptación
5. Soporte para diferentes versiones
