#!/bin/bash

# Script para generar archivo Docker Compose con cantidad configurable de clientes
# Uso: ./generar-compose.sh <archivo_salida> <cantidad_clientes>

# Verificar que se proporcionen los parámetros necesarios
if [ $# -ne 2 ]; then
    echo "Error: Se requieren exactamente 2 parámetros"
    echo "Uso: $0 <archivo_salida> <cantidad_clientes>"
    echo "Ejemplo: $0 docker-compose-dev.yaml 5"
    exit 1
fi

ARCHIVO_SALIDA="$1"
CANTIDAD_CLIENTES="$2"

# Verificar que la cantidad de clientes sea un número válido
if ! [[ "$CANTIDAD_CLIENTES" =~ ^[0-9]+$ ]] || [ "$CANTIDAD_CLIENTES" -lt 0 ]; then
    echo "Error: La cantidad de clientes debe ser un número entero no negativo"
    exit 1
fi

echo "Generando archivo Docker Compose: $ARCHIVO_SALIDA"
echo "Cantidad de clientes: $CANTIDAD_CLIENTES"

# Crear el archivo Docker Compose
cat > "$ARCHIVO_SALIDA" << EOF
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./server/config.ini:/config.ini:ro
    networks:
      - testing_net
EOF

# Agregar los clientes dinámicamente
for i in $(seq 1 $CANTIDAD_CLIENTES); do
    cat >> "$ARCHIVO_SALIDA" << EOF

  client$i:
    container_name: client$i
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=$i
    volumes:
      - ./client/config.yaml:/config.yaml:ro
    networks:
      - testing_net
    depends_on:
      - server
EOF
done

# Agregar la configuración de red al final
cat >> "$ARCHIVO_SALIDA" << EOF

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
EOF

echo "Archivo $ARCHIVO_SALIDA generado exitosamente con $CANTIDAD_CLIENTES clientes"
