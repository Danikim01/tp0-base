#!/bin/bash

echo "=== Sistema de Quiniela - Test ==="

# Construir las imágenes
echo "Construyendo imágenes..."
docker build -f ./server/Dockerfile -t "server:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .

# Ejecutar el sistema
echo "Ejecutando sistema de quiniela..."
docker compose -f docker-compose-quiniela.yaml up -d --build

echo "=== Test completado ==="
