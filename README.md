# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Quick Start

### Ejecución Rápida con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd tp0-base

# 2. Iniciar el sistema completo
make docker-compose-up

# 3. Ver los logs
make docker-compose-logs

# 4. Detener el sistema
make docker-compose-down
```

### Ejecución Local (con 1 cliente)

```bash
# 1. Compilar el cliente
make build

# 2. Iniciar servidor (terminal 1)
cd server && python3 main.py

# 3. Iniciar cliente (terminal 2)
# Desde el directorio raíz del proyecto hay que setear las variables de entorno y ejecutar el cliente:
export NOMBRE="Santiago Lionel"
export APELLIDO="Lorca"
export DOCUMENTO="30904465"
export NACIMIENTO="1999-03-17"
export NUMERO="7574"
export CLI_ID="1"
export CLI_SERVER_ADDRESS="localhost:12345"
export CLI_LOOP_AMOUNT="5"
export CLI_LOOP_PERIOD="5s"
export CLI_LOG_LEVEL="INFO"
./bin/client
```

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

#### Pasos para ejecutar con Docker:

1. **Iniciar el sistema completo:**
   ```bash
   make docker-compose-up
   ```

2. **Ver los logs en tiempo real:**
   ```bash
   make docker-compose-logs
   ```

3. **Detener el sistema:**
   ```bash
   make docker-compose-down
   ```

### Ejecución Local (Desarrollo)

Si prefieres ejecutar el sistema localmente sin Docker, sigue estos pasos:

#### Prerrequisitos:
- **Python 3.9+** instalado
- **Go 1.19+** instalado
- **Git** para clonar el repositorio

#### Pasos para ejecución local:

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd tp0-base
   ```

2. **Instalar dependencias Python:**
   ```bash
   cd server
   pip install -r requirements.txt  # si existe
   cd ..
   ```

3. **Compilar el cliente Go:**
   ```bash
   make build
   ```

4. **Iniciar el servidor (en una terminal):**
   ```bash
   cd server
   python3 main.py
   ```

5. **Iniciar el cliente (en otra terminal):**
   ```bash
   # Desde el directorio raíz del proyecto:
   # Configurar variables de entorno para la apuesta:
   export NOMBRE="Santiago Lionel"
   export APELLIDO="Lorca"
   export DOCUMENTO="30904465"
   export NACIMIENTO="1999-03-17"
   export NUMERO="7574"
   
   # Configurar variables de entorno del cliente:
   export CLI_ID="1"
   export CLI_SERVER_ADDRESS="localhost:12345"
   export CLI_LOOP_AMOUNT="5"
   export CLI_LOOP_PERIOD="5s"
   export CLI_LOG_LEVEL="INFO"
   
   # Ejecutar el cliente:
   ./bin/client
   ```

#### Configuración local:

**Servidor (Python):**
- Puerto por defecto: `12345`
- Archivo de configuración: `server/config.ini`
- Variables de entorno disponibles:
  - `SERVER_PORT`: Puerto del servidor
  - `SERVER_LISTEN_BACKLOG`: Backlog de conexiones
  - `LOGGING_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

**Cliente (Go):**
- Archivo de configuración: `client/config.yaml`
- Variables de entorno disponibles:
  - `CLI_ID`: ID del cliente
  - `CLI_SERVER_ADDRESS`: Dirección del servidor (`server:12345`)
  - `CLI_LOOP_AMOUNT`: Cantidad de mensajes a enviar
  - `CLI_LOOP_PERIOD`: Período entre mensajes (ej: `5s`, `150ms`)
  - `CLI_LOG_LEVEL`: Nivel de logging

### Configuración de Variables de Entorno

#### Para el Cliente (Agencia de Quiniela):
```bash
# Variables de la apuesta:
export NOMBRE="Santiago Lionel"
export APELLIDO="Lorca"
export DOCUMENTO="30904465"
export NACIMIENTO="1999-03-17"
export NUMERO="7574"

# Variables de configuración del cliente:
export CLI_ID="1"
export CLI_SERVER_ADDRESS="localhost:12345"
export CLI_LOOP_AMOUNT="5"
export CLI_LOOP_PERIOD="5s"
export CLI_LOG_LEVEL="INFO"
```

#### Para el Servidor:
```bash
export SERVER_PORT="12345"
export SERVER_LISTEN_BACKLOG="5"
export LOGGING_LEVEL="INFO"
```

### Monitoreo y Debugging

#### Ver logs del sistema:
```bash
# Con Docker
make docker-compose-logs

# Filtrar logs específicos
make docker-compose-logs | grep "apuesta_enviada"
make docker-compose-logs | grep "apuesta_almacenada"
```

#### Verificar estado de containers:
```bash
docker ps
docker logs server
docker logs client1
```

### Ejemplo de Ejecución Completa

```bash
# 1. Iniciar el sistema
make docker-compose-up

# 2. Ver logs
make docker-compose-logs

# 3. Detener el sistema
make docker-compose-down
```

**Salida esperada:**
```
client1  | action: apuesta_enviada | result: success | dni: 30904465 | numero: 7574
server   | action: apuesta_almacenada | result: success | dni: 30904465 | numero: 7574
```

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bets(...)` para control futuro de ganadores. La función `store_bets(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).

## Ejercicio 6: Procesamiento por Batches

### Descripción General

Se ha implementado el procesamiento por batches (chunks) que permite enviar múltiples apuestas en una sola consulta, optimizando los tiempos de transmisión y procesamiento.

### Características Principales

- **Procesamiento por Batches**: Envío de múltiples apuestas en una sola transacción
- **Archivos CSV**: Lectura de apuestas desde archivos numerados por agencia
- **Volúmenes Docker**: Persistencia de datos fuera de las imágenes
- **Configuración Flexible**: Tamaño máximo de batch configurable
- **Logs Detallados**: Seguimiento completo del procesamiento

### Estructura de Archivos

```
.data/
├── agency-1.csv    # Apuestas de la agencia 1
├── agency-2.csv    # Apuestas de la agencia 2
└── agency-N.csv    # Apuestas de la agencia N
```

### Formato CSV

```csv
Name,Surname,00000000,2000-01-01,7574
Name,Surname,00000001,2000-01-01,1
Name,Surname,00000002,2000-01-01,2
```

**Nota**: El formato CSV de los tests no incluye el campo `agency` explícitamente. El sistema extrae automáticamente el ID de la agencia del nombre del archivo (`agency-N.csv`).

### Configuración de Batches

```yaml
batch:
  maxAmount: 50  # Máximo 50 apuestas por batch (ajustado para < 8KB)
```

### Logs del Servidor

- **Éxito**: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD}`
- **Error**: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD}`

### Logs del Cliente

- **Batch Exitoso**: `action: batch_processed | result: success | cantidad: ${CANTIDAD}`
- **Batch Fallido**: `action: batch_processed | result: fail | cantidad: ${CANTIDAD}`

## Ejercicio 7: Sorteo y Consulta de Ganadores

### Descripción General

Se ha implementado el sistema de sorteo y consulta de ganadores por agencia, con soporte dinámico para cualquier cantidad de agencias.

### Características Principales

- **Sorteo Dinámico**: El servidor espera la notificación de finalización de al menos una agencia
- **Consulta por Agencia**: Cada agencia puede consultar únicamente sus ganadores
- **Persistencia**: Las apuestas se almacenan con identificación de agencia
- **Sincronización**: Control de estado del sorteo con mutexes

### Flujo del Sorteo

1. **Envío de Apuestas**: Los clientes envían apuestas en batches
2. **Notificación de Finalización**: Cada cliente notifica al servidor cuando termina
3. **Activación del Sorteo**: El servidor activa el sorteo cuando recibe la primera notificación
4. **Consulta de Ganadores**: Los clientes consultan sus ganadores específicos

### Protocolo de Notificación y Consulta

#### Notificación de Finalización
```go
// Cliente envía notificación
protocol.SendFinishedNotification(conn, agencyID)

// Servidor responde
protocol.send_finished_ack(client_sock, success)
```

#### Consulta de Ganadores
```go
// Cliente consulta ganadores
protocol.SendWinnersQuery(conn, agencyID)

// Servidor responde con lista de DNIs ganadores
protocol.send_winners_response(client_sock, winners)
```

### Manejo de Agencias

#### Extracción Automática de Agency ID
```go
func extractAgencyID(filename string) string {
    // Extrae el ID de la agencia del nombre del archivo agency-N.csv
    parts := strings.Split(filename, "/")
    if len(parts) > 0 {
        lastPart := parts[len(parts)-1]
        if strings.HasPrefix(lastPart, "agency-") && strings.HasSuffix(lastPart, ".csv") {
            agencyID := strings.TrimPrefix(lastPart, "agency-")
            agencyID = strings.TrimSuffix(agencyID, ".csv")
            return agencyID
        }
    }
    return "1" // Por defecto
}
```

#### Almacenamiento con Agency
```python
# Servidor almacena apuestas con agency
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                            bet.document, bet.birthdate, bet.number])
```

#### Consulta de Ganadores por Agencia
```python
def _get_winners_for_agency(self, agency_id: str) -> list[str]:
    winners = []
    for bet in load_bets():
        if str(bet.agency) == agency_id and has_won(bet):
            winners.append(bet.document)
    return winners
```

### Cambios Implementados para Solucionar Problemas

#### Cambios en el Protocolo

**Antes**:
```go
type Bet struct {
    Nombre     string
    Apellido   string
    DNI        string
    Nacimiento string
    Numero     string
}
```

**Después**:
```go
type Bet struct {
    Agency     string  // Nuevo campo
    Nombre     string
    Apellido   string
    DNI        string
    Nacimiento string
    Numero     string
}
```

**Codificación Actualizada**:
```go
// Cliente
payload = append(payload, p.encodeString(bet.Agency)...)    // Nuevo campo
payload = append(payload, p.encodeString(bet.Nombre)...)
// ... resto de campos

// Servidor
payload += self._encode_string(str(bet.agency))  // Nuevo campo
payload += self._encode_string(bet.first_name)
// ... resto de campos
```

### Funciones Principales del Protocolo

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

### Manejo de Errores

#### Validaciones Implementadas
1. **Longitud de mensaje**: Máximo 8KB para evitar ataques DoS
2. **Delimitador**: Verificación del byte delimitador
3. **Datos completos**: Lectura/escritura exacta de bytes
4. **Tipos de mensaje**: Validación de tipos válidos
5. **Strings**: Verificación de longitud y codificación UTF-8

#### Códigos de Error
- Conexión cerrada inesperadamente
- Mensaje demasiado grande
- Delimitador inválido
- Payload incompleto
- Tipo de mensaje desconocido
- Error de codificación/decodificación

### Configuración del Protocolo

El protocolo está configurado para:
- **Puerto**: 12345 (configurable)
- **Tamaño máximo**: 8KB por mensaje
- **Timeout**: Sin timeout específico (usa configuración del socket)
- **Codificación**: UTF-8 para strings

#### Configuración de Batches

```yaml
batch:
  maxAmount: 50  # Máximo 50 apuestas por batch (ajustado para < 8KB)
```

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

### Logs del Protocolo

El protocolo genera logs detallados para debugging:

#### Logs de Batches

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

#### Logs de Error en Batches
```
action: apuesta_recibida | result: fail | cantidad: 10
action: batch_processed | result: fail | client_id: 1 | batch: 1-10 | cantidad: 10
```

### Configuración de Volúmenes Docker

```yaml
volumes:
  - ./.data:/data:ro  # Montaje de archivos CSV
```

Los archivos CSV se montan como volúmenes de solo lectura para:
- Persistencia de datos fuera de las imágenes
- Fácil actualización de datos sin reconstruir imágenes
- Separación de datos de la lógica de aplicación

## Protocolo de Comunicación Implementado

### Descripción General

Se ha implementado un protocolo binario eficiente y robusto que soporta tanto apuestas individuales como batches, con soporte completo para identificación de agencias.

### Características Principales

- **Sincronización**: Uso de mutexes para acceso a recursos compartidos
- **Cierre de FDs**: Manejo graceful de conexiones y recursos
- **Control de bytes**: Lectura/escritura exacta evitando short-read/short-write
- **Manejo de errores**: Validación completa de mensajes y conexiones
- **Identificación de Agencias**: Soporte completo para múltiples agencias con tracking individual

### Estructura del Protocolo

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
- `0x01`: Apuesta individual (MSG_BET)
- `0x02`: Batch de apuestas (MSG_BATCH)
- `0x03`: Respuesta de éxito (MSG_SUCCESS)
- `0x04`: Respuesta de error (MSG_ERROR)
- `0x05`: Notificación de finalización (MSG_FINISHED)
- `0x06`: Consulta de ganadores (MSG_WINNERS_QUERY)
- `0x07`: Respuesta con ganadores (MSG_WINNERS_RESPONSE)

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

### Formato del Payload

**Apuesta Individual (Tipo 0x01):**
```
[AGENCY_LEN][AGENCY][NOMBRE_LEN][NOMBRE][APELLIDO_LEN][APELLIDO][DNI_LEN][DNI][NACIMIENTO_LEN][NACIMIENTO][NUMERO_LEN][NUMERO]
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

**Notificación de Finalización (Tipo 0x05):**
```
[AGENCY_ID_LEN][AGENCY_ID]
```

**Consulta de Ganadores (Tipo 0x06):**
```
[AGENCY_ID_LEN][AGENCY_ID]
```

**Respuesta con Ganadores (Tipo 0x07):**
```
[CANTIDAD_GANADORES][DNI_1_LEN][DNI_1][DNI_2_LEN][DNI_2]...[DNI_N_LEN][DNI_N]
```

### Estructura de Datos

#### Estructura de Apuesta (Actualizada)

```go
type Bet struct {
    Agency     string  // ID de la agencia (nuevo campo)
    Nombre     string
    Apellido   string
    DNI        string
    Nacimiento string
    Numero     string
}
```

#### Codificación de Apuesta

```go
// Cliente (Go)
func (p *Protocol) EncodeBet(bet Bet) []byte {
    payload := make([]byte, 0)
    payload = append(payload, p.encodeString(bet.Agency)...)    // Nuevo campo
    payload = append(payload, p.encodeString(bet.Nombre)...)
    payload = append(payload, p.encodeString(bet.Apellido)...)
    payload = append(payload, p.encodeString(bet.DNI)...)
    payload = append(payload, p.encodeString(bet.Nacimiento)...)
    payload = append(payload, p.encodeString(bet.Numero)...)
    return payload
}
```

```python
# Servidor (Python)
def encode_bet(self, bet: Bet) -> bytes:
    payload = b""
    payload += self._encode_string(str(bet.agency))  # Nuevo campo
    payload += self._encode_string(bet.first_name)
    payload += self._encode_string(bet.last_name)
    payload += self._encode_string(bet.document)
    payload += self._encode_string(bet.birthdate.isoformat())
    payload += self._encode_string(str(bet.number))
    return payload
```

```
[LONGITUD][TIPO][PAYLOAD][DELIMITADOR]
```

- **Header (5 bytes)**: 4 bytes longitud (uint32, big-endian) + 1 byte tipo
- **Payload**: Datos del mensaje (longitud variable)
- **Delimitador**: 1 byte con valor `0xFF`

### Tipos de Mensaje

| Tipo | Valor | Descripción |
|------|-------|-------------|
| MSG_BET | 0x01 | Apuesta individual |
| MSG_BATCH | 0x02 | Batch de apuestas |
| MSG_SUCCESS | 0x03 | Respuesta de éxito |
| MSG_ERROR | 0x04 | Respuesta de error |

### Formato de Datos

#### Codificación de Strings
Cada string se codifica como `[LONGITUD_STRING][DATOS_STRING]`:
- **Longitud**: 2 bytes (uint16, big-endian)
- **Datos**: Bytes UTF-8 del string

#### Apuesta Individual (MSG_BET)
```
[NOMBRE_LEN][NOMBRE][APELLIDO_LEN][APELLIDO][DNI_LEN][DNI][NACIMIENTO_LEN][NACIMIENTO][NUMERO_LEN][NUMERO]
```

#### Respuesta (MSG_SUCCESS/MSG_ERROR)
```
[DNI_LEN][DNI][NUMERO_LEN][NUMERO]
```

### Manejo de Errores

#### Validaciones Implementadas
1. **Longitud de mensaje**: Máximo 8KB
2. **Delimitador**: Verificación del byte delimitador
3. **Datos completos**: Lectura/escritura exacta de bytes
4. **Tipos de mensaje**: Validación de tipos válidos
5. **Strings**: Verificación de longitud y codificación UTF-8

#### Códigos de Error
- Conexión cerrada inesperadamente
- Mensaje demasiado grande
- Delimitador inválido
- Payload incompleto
- Tipo de mensaje desconocido
- Error de codificación/decodificación

### Configuración

El protocolo está configurado para:
- **Puerto**: 12345 (configurable)
- **Tamaño máximo**: 8KB por mensaje
- **Timeout**: Sin timeout específico (usa configuración del socket)
- **Codificación**: UTF-8 para strings

## Mecanismos de Sincronización

### Cliente (Go)
- **Mutex**: Protege acceso a la conexión del socket
- **Context**: Manejo de cancelación graceful
- **Signal handlers**: Captura de SIGTERM/SIGINT
- **Retry automático**: Sistema de reintentos para consulta de ganadores

### Servidor (Python)
- **Threading**: Preparado para múltiples conexiones concurrentes
- **Locks**: Protección de recursos compartidos
- **Graceful shutdown**: Cierre ordenado de conexiones
- **Estado compartido**: Control de agencias finalizadas y estado del sorteo

## Mecanismo de Retry

### Cliente - Consulta de Ganadores con Retry

El cliente implementa un sistema robusto de reintentos automáticos para la consulta de ganadores:

```go
func (c *Client) queryWinnersWithRetry() ([]string, error) {
    maxRetries := 300
    retryDelay := time.Second * 2
    
    for attempt := 1; attempt <= maxRetries; attempt++ {
        // Crear nueva conexión para cada intento
        if err := c.createClientSocket(); err != nil {
            return nil, err
        }
        
        // Consultar ganadores
        if err := c.protocol.SendWinnersQuery(c.conn, c.config.ID); err != nil {
            c.closeClientSocket()
            return nil, err
        }
        
        // Recibir respuesta
        msgType, _, err := c.protocol.ReceiveMessage(c.conn)
        c.closeClientSocket()
        
        switch msgType {
        case MSG_WINNERS_RESPONSE:
            // Procesar ganadores y retornar
            return winners, nil
            
        case MSG_RETRY:
            // El servidor indica que debe esperar
            if attempt < maxRetries {
                time.Sleep(retryDelay)
                continue
            }
        }
    }
    
    return nil, fmt.Errorf("máximo número de reintentos alcanzado")
}
```

**Características del retry:**
- **Máximo 300 intentos** con delay de 2 segundos entre intentos
- **Nueva conexión por intento** para evitar problemas de socket
- **Manejo de mensaje MSG_RETRY** del servidor
- **Logs detallados** de cada intento y resultado

### Servidor - Respuesta de Retry

El servidor responde con `MSG_RETRY` cuando el sorteo aún no está completo:

```python
def send_retry_response(self, client_sock: socket.socket, message: str = "Lottery not completed yet") -> bool:
    """
    Envía respuesta de retry al cliente indicando que debe esperar
    """
    payload = self._encode_string(message)
    return self.send_message(client_sock, self.MSG_RETRY, payload)
```

**Lógica del servidor:**
- Verifica si todas las agencias han finalizado (`len(self._finished_agencies) >= self._expected_agencies`)
- Si no están todas finalizadas, envía `MSG_RETRY` con mensaje informativo
- Si están todas finalizadas, procesa y envía los ganadores

## Uso de Locks en Servidor No Concurrente

Aunque el servidor actual no implementa concurrencia (una conexión por vez), se utilizan locks por las siguientes razones:

### 1. **Preparación para Concurrencia Futura**
```python
# Locks preparados para cuando se implemente threading
self._connections_lock = threading.Lock()  # Para lista de conexiones activas
self._threads_lock = threading.Lock()      # Para pool de threads
self._storage_lock = threading.Lock()      # Para operaciones de persistencia
self._state_lock = threading.Lock()        # Para estado del sorteo
```

### 2. **Protección de Estado Compartido**
```python
def _mark_agency_finished(self, agency_id: str):
    """Marca una agencia como finalizada y verifica si todas terminaron"""
    with self._state_lock:
        self._finished_agencies.add(agency_id)
        logging.info(f'action: agency_finished | result: success | agency: {agency_id}')
```

### 3. **Operaciones de Persistencia**
```python
# Las funciones de la cátedra (store_bets, load_bets, has_won) 
# pueden no ser thread-safe, por lo que se protegen con locks
with self._storage_lock:
    store_bets([bet])
```

### 4. **Graceful Shutdown Thread-Safe**
```python
def _graceful_shutdown(self):
    """Perform graceful shutdown of all resources"""
    with self._connections_lock:
        for client_sock in self._active_connections:
            try:
                client_sock.close()
            except Exception as e:
                logging.error(f'action: close_client_connection | result: fail | error: {e}')
```

### 5. **Detección Automática de Agencias**
```python
def _detect_expected_agencies(self) -> int:
    """Detecta automáticamente cuántas agencias se esperan"""
    try:
        # Usar variable de entorno EXPECTED_AGENCIES
        env_count = os.environ.get('EXPECTED_AGENCIES')
        if env_count:
            return int(env_count)
        
        # Fallback: detectar archivos CSV disponibles
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '.data')
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.startswith('agency-') and f.endswith('.csv')]
            return len(csv_files)
        
        return 5  # Valor por defecto
    except Exception:
        return 5  # Valor por defecto en caso de error
```

## Graceful Shutdown Mejorado

### Cliente (Go)
```go
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

func (c *Client) gracefulShutdown() {
    log.Info("action: graceful_shutdown | result: in_progress")
    
    // Cancelar contexto para interrumpir loops
    c.cancel()
    
    // Cerrar conexión si está abierta
    if c.conn != nil {
        c.conn.Close()
        log.Info("action: close_connection | result: success")
    }
    
    log.Info("action: graceful_shutdown | result: success")
}
```

### Servidor (Python)
```python
def _signal_handler(self, signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info(f'action: signal_received | result: success | signal: {signum}')
    self._shutdown_requested = True
    self._graceful_shutdown()
    sys.exit(0)

def _graceful_shutdown(self):
    """Perform graceful shutdown of all resources"""
    logging.info('action: graceful_shutdown | result: in_progress')
    
    # Close all active client connections
    with self._connections_lock:
        for client_sock in self._active_connections:
            try:
                client_sock.close()
                logging.info('action: close_client_connection | result: success')
            except Exception as e:
                logging.error(f'action: close_client_connection | result: fail | error: {e}')
    
    # Close server socket
    try:
        self._server_socket.close()
        logging.info('action: close_server_socket | result: success')
    except Exception as e:
        logging.error(f'action: close_server_socket | result: fail | error: {e}')
    
    logging.info('action: graceful_shutdown | result: success')
```

## Logs de Retry y Sincronización

### Logs del Cliente
```
action: retry_message | result: success | client_id: 1 | attempt: 1 | message: Lottery not completed yet. 2/5 agencies finished.
action: retry_wait | result: in_progress | client_id: 1 | attempt: 1/300 | delay: 2s
action: consulta_ganadores | result: success | cant_ganadores: 3
```

### Logs del Servidor
```
action: sorteo | result: in_progress | agencies_finished: 2/5
action: sorteo | result: success
action: agency_finished | result: success | agency: 1
action: agency_finished | result: success | agency: 2
```
