#!/bin/bash

# Script para validar el funcionamiento del echo server usando netcat
# El script se ejecuta dentro de la red Docker para comunicarse con el servidor

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Función para imprimir mensajes de error
print_error() {
    echo -e "${RED}action: test_echo_server | result: fail${NC}"
    echo "Error: $1" >&2
}

# Función para imprimir mensajes de éxito
print_success() {
    echo -e "${GREEN}action: test_echo_server | result: success${NC}"
}

# Verificar que algún servidor esté ejecutándose
echo "Verificando que el servidor esté ejecutándose..."

# Buscar cualquier contenedor llamado "server" que esté ejecutándose
if ! docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "^server.*Up"; then
    print_error "El servidor no está ejecutándose. Ejecuta 'docker-compose up -d' primero."
    exit 1
fi

echo "Servidor detectado. Iniciando validación..."

# Mensaje de prueba
TEST_MESSAGE="Hello Echo Server Test 12345"

# Crear un contenedor temporal con netcat para conectarse al servidor
# Usar la misma red que el servidor para poder comunicarse
echo "Enviando mensaje de prueba: '$TEST_MESSAGE'"

# Ejecutar netcat dentro de un contenedor temporal conectado a la misma red
# Redirigir stderr a /dev/null para evitar mensajes de instalación
RESULT=$(docker run --rm \
    --network tp0_testing_net \
    alpine:latest \
    sh -c "
        # Instalar netcat (redirigir salida a /dev/null)
        apk add --no-cache netcat-openbsd > /dev/null 2>&1
        
        # Enviar mensaje y capturar respuesta
        echo '$TEST_MESSAGE' | nc server 12345
    " 2>/dev/null)

# Verificar el resultado
if [ $? -eq 0 ] && [ "$RESULT" = "$TEST_MESSAGE" ]; then
    echo "Mensaje enviado: $TEST_MESSAGE"
    echo "Respuesta recibida: $RESULT"
    print_success
else
    echo "Mensaje enviado: $TEST_MESSAGE"
    echo "Respuesta recibida: $RESULT"
    print_error "El servidor no respondió correctamente. Respuesta esperada: '$TEST_MESSAGE', Respuesta recibida: '$RESULT'"
    exit 1
fi
