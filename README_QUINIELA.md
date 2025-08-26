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

### Mensaje de Apuesta (Cliente → Servidor)
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

### Respuesta del Servidor (Servidor → Cliente)
```json
{
  "type": "bet_response",
  "status": "success",
  "dni": "30904465",
  "numero": "7574"
}
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

