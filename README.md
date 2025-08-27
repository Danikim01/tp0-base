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
  - `CLI_SERVER_ADDRESS`: Dirección del servidor (`localhost:12345` para local, `server:12345` para Docker)
  - `CLI_LOOP_AMOUNT`: Cantidad de mensajes a enviar
  - `CLI_LOOP_PERIOD`: Período entre mensajes (ej: `5s`, `150ms`)
  - `CLI_LOG_LEVEL`: Nivel de logging
- **Importante**: Para ejecución local, usar `localhost:12345`. Para Docker, usar `server:12345`

### 🔧 Configuración de Variables de Entorno

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

### 📊 Monitoreo y Debugging

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

### 📝 Ejemplo de Ejecución Completa

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

### 🚨 Solución de Problemas

#### Problema: `./bin/client: No such file or directory`
```bash
# Asegúrate de estar en el directorio raíz del proyecto
pwd  # Debería mostrar: /path/to/tp0-base

# Si no existe el binario, compílalo:
make build

# Verifica que existe:
ls -la bin/client
```

#### Problema: `Could not parse CLI_LOOP_PERIOD env var as time.Duration`
```bash
# Asegúrate de configurar todas las variables de entorno del cliente:
export CLI_ID="1"
export CLI_SERVER_ADDRESS="localhost:12345"
export CLI_LOOP_AMOUNT="5"
export CLI_LOOP_PERIOD="5s"  # Formato correcto: "5s", "150ms", etc.
export CLI_LOG_LEVEL="INFO"
```

#### Problema: Puerto ya en uso
```bash
# Verificar qué está usando el puerto
sudo netstat -tulpn | grep :12345

# Cambiar puerto en configuración
export SERVER_PORT="12346"
```

#### Problema: Permisos de Docker
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión
```

#### Problema: Imágenes no se construyen
```bash
# Limpiar y reconstruir
make docker-compose-down
docker system prune -f
make docker-compose-up
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

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


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
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
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
agency,first_name,last_name,document,birthdate,number
1,Juan,Pérez,12345678,1990-01-01,1234
1,María,González,23456789,1985-05-15,5678
```

### Configuración de Batches

```yaml
batch:
  maxAmount: 50  # Máximo 50 apuestas por batch (ajustado para < 8KB)
```

### Almacenamiento de Apuestas

Las apuestas procesadas se almacenan en:
- **Local**: `./server/data/bets.csv`
- **Docker**: `/server_data/bets.csv` (dentro del contenedor)

El directorio `server/data/` se incluye en el repositorio para asegurar que funcione correctamente cuando alguien clone el proyecto. El archivo `bets.csv` se ignora en Git para evitar conflictos entre diferentes ejecuciones.

### Logs del Servidor

- **Éxito**: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD}`
- **Error**: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD}`

### Logs del Cliente

- **Batch Exitoso**: `action: batch_processed | result: success | cantidad: ${CANTIDAD}`
- **Batch Fallido**: `action: batch_processed | result: fail | cantidad: ${CANTIDAD}`

## Protocolo de Comunicación Implementado

### Descripción General

Se ha implementado un protocolo binario eficiente y robusto que soporta tanto apuestas individuales como batches.

### Características Principales

- **Sincronización**: Uso de mutexes para acceso a recursos compartidos
- **Cierre de FDs**: Manejo graceful de conexiones y recursos
- **Control de bytes**: Lectura/escritura exacta evitando short-read/short-write
- **Manejo de errores**: Validación completa de mensajes y conexiones

### Estructura del Protocolo

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

### Documentación Detallada

Para más detalles sobre el protocolo, consultar el archivo `PROTOCOLO.md` que incluye:
- Ejemplos de uso completos
- Funciones principales del protocolo
- Guías de implementación
- Casos de prueba

## Mecanismos de Sincronización

### Cliente (Go)
- **Mutex**: Protege acceso a la conexión del socket
- **Context**: Manejo de cancelación graceful
- **Signal handlers**: Captura de SIGTERM/SIGINT

### Servidor (Python)
- **Threading**: Preparado para múltiples conexiones concurrentes
- **Locks**: Protección de recursos compartidos
- **Graceful shutdown**: Cierre ordenado de conexiones
