# Sistema de Quiniela - TP0

## Descripción

Este sistema implementa un servicio de quiniela distribuido donde:

- **Clientes**: 5 agencias de quiniela que envían apuestas
- **Servidor**: Central de Lotería Nacional que recibe y almacena las apuestas

## Arquitectura

### Cliente (Agencias)
- Implementado en Go
- Recibe datos de apuesta como variables de entorno
- Envía apuestas al servidor usando un protocolo JSON
- Maneja errores de comunicación (short-write, short-read)

### Servidor (Central)
- Implementado en Python
- Recibe apuestas de múltiples agencias
- Almacena apuestas usando la función `store_bet()`
- Responde con confirmación de almacenamiento

## Protocolo de Comunicación

El protocolo implementa un sistema de comunicación cliente-servidor basado en **JSON sobre TCP** con las siguientes características técnicas:

### Especificaciones del Protocolo

#### 1. **Formato de Mensajes**
- **Codificación**: UTF-8
- **Serialización**: JSON
- **Delimitador**: Carácter de nueva línea (`\n`)
- **Transporte**: TCP/IP

#### 2. **Estructura de Mensajes**

##### Mensaje de Apuesta (Cliente → Servidor)
```json
{
  "type": "bet",
  "bet": {
    "nombre": "Santiago Lionel",
    "apellido": "Lorca", 
    "dni": "30904465",
    "nacimiento": "1999-03-17",
    "numero": "7574"
  }
}
```

**Campos Obligatorios:**
- `type`: Debe ser exactamente "bet"
- `bet.nombre`: Nombre del apostador (string)
- `bet.apellido`: Apellido del apostador (string)
- `bet.dni`: Documento Nacional de Identidad (string)
- `bet.nacimiento`: Fecha de nacimiento en formato ISO (YYYY-MM-DD)
- `bet.numero`: Número apostado (string que representa un entero)

##### Respuesta del Servidor (Servidor → Cliente)
```json
{
  "type": "bet_response",
  "status": "success",
  "dni": "30904465",
  "numero": "7574"
}
```

**Campos de Respuesta:**
- `type`: Siempre "bet_response"
- `status`: "success" o "error"
- `dni`: DNI del apostador (echo del mensaje original)
- `numero`: Número apostado (echo del mensaje original)

#### 3. **Manejo de Errores de Comunicación**

##### Short-Read (Recepción Incompleta)
- **Problema**: Un mensaje puede llegar fragmentado en múltiples paquetes TCP
- **Solución**: El servidor lee hasta encontrar el delimitador `\n`
- **Implementación**: Loop que acumula datos hasta completar el mensaje

```python
data = b""
while not data.endswith(b'\n'):
    chunk = client_sock.recv(1024)
    if not chunk:
        return None  # Conexión cerrada
    data += chunk
```

##### Short-Write (Escritura Incompleta)
- **Problema**: Un mensaje puede no enviarse completamente en una sola operación
- **Solución**: Loop que asegura el envío completo del mensaje
- **Implementación**: Control de bytes enviados vs bytes totales

```python
total_sent = 0
while total_sent < len(message):
    sent = client_sock.send(message[total_sent:])
    if sent == 0:
        return False  # Conexión rota
    total_sent += sent
```

#### 4. **Validación de Mensajes**

##### Validaciones del Servidor
1. **Formato JSON**: Verificación de sintaxis JSON válida
2. **Tipo de Mensaje**: Confirmación de `type: "bet"`
3. **Campos Obligatorios**: Presencia de todos los campos requeridos
4. **Formato de Fecha**: Validación de formato ISO (YYYY-MM-DD)
5. **Formato de Número**: Verificación de que sea un entero válido

##### Casos de Error
- **JSON Inválido**: Error de parsing
- **Tipo Incorrecto**: Mensaje no reconocido
- **Campos Faltantes**: Datos incompletos
- **Formato Inválido**: Fechas o números mal formateados

#### 5. **Estados de Respuesta**

| Status | Descripción | Condición |
|--------|-------------|-----------|
| `success` | Apuesta almacenada correctamente | Todos los datos son válidos y se guarda exitosamente |
| `error` | Error en el procesamiento | Datos inválidos o error interno del servidor |

#### 6. **Flujo de Comunicación**

```
Cliente                    Servidor
   |                         |
   |--- Mensaje JSON ------->|
   |                         |-- Validar formato
   |                         |-- Validar campos
   |                         |-- Almacenar apuesta
   |                         |-- Generar respuesta
   |<-- Respuesta JSON ------|
   |                         |
```

## Variables de Entorno del Cliente

- `NOMBRE`: Nombre del apostador
- `APELLIDO`: Apellido del apostador  
- `DOCUMENTO`: DNI del apostador
- `NACIMIENTO`: Fecha de nacimiento (YYYY-MM-DD)
- `NUMERO`: Número apostado

## Logs del Sistema

### Cliente
```
action: apuesta_enviada | result: success | dni: 30904465 | numero: 7574
```

### Servidor
```
action: apuesta_almacenada | result: success | dni: 30904465 | numero: 7574
```


## Características Técnicas

### Manejo de Errores
- **Short-write**: Evitado usando loops de escritura completa
- **Short-read**: Evitado usando delimitadores de mensaje
- **Graceful shutdown**: Manejo correcto de señales SIGTERM/SIGINT

### Serialización
- Protocolo JSON para intercambio de datos
- Delimitadores de línea para separación de mensajes
- Validación de tipos de mensaje

### Separación de Responsabilidades
- **Protocolo**: Manejo de comunicación y serialización
- **Modelo**: Estructuras de datos de apuestas
- **Negocio**: Lógica de almacenamiento y validación

