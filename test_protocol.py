#!/usr/bin/env python3
"""
Script de prueba para validar el protocolo de comunicación propio
"""

import socket
import struct
import threading
import time
import logging
from server.common.protocol import Protocol
from server.common.utils import Bet

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def test_protocol_encoding():
    """Prueba la codificación y decodificación del protocolo"""
    print("=== Prueba de Codificación/Decodificación ===")
    
    protocol = Protocol()
    
    # Crear apuesta de prueba
    bet = Bet(
        agency="1",
        first_name="Juan",
        last_name="Pérez",
        document="12345678",
        birthdate="1990-01-01",
        number="1234"
    )
    
    # Codificar apuesta
    encoded = protocol.encode_bet(bet)
    print(f"Apuesta codificada: {len(encoded)} bytes")
    
    # Decodificar apuesta
    decoded = protocol.decode_bet(encoded)
    
    if decoded:
        print(f"Decodificación exitosa:")
        print(f"  Nombre: {decoded.first_name}")
        print(f"  Apellido: {decoded.last_name}")
        print(f"  DNI: {decoded.document}")
        print(f"  Nacimiento: {decoded.birthdate}")
        print(f"  Número: {decoded.number}")
    else:
        print("❌ Error en decodificación")
        return False
    
    return True

def test_message_structure():
    """Prueba la estructura de mensajes"""
    print("\n=== Prueba de Estructura de Mensajes ===")
    
    protocol = Protocol()
    
    # Crear mensaje de prueba
    payload = b"test payload"
    msg_type = Protocol.MSG_BET
    
    # Construir mensaje completo
    header = struct.pack('!IB', len(payload), msg_type)
    message = header + payload + Protocol.DELIMITER
    
    print(f"Header: {len(header)} bytes")
    print(f"Payload: {len(payload)} bytes")
    print(f"Delimitador: {len(Protocol.DELIMITER)} bytes")
    print(f"Mensaje total: {len(message)} bytes")
    
    # Verificar estructura
    if len(message) == Protocol.HEADER_SIZE + len(payload) + 1:
        print("✅ Estructura de mensaje correcta")
        return True
    else:
        print("❌ Estructura de mensaje incorrecta")
        return False

def test_string_encoding():
    """Prueba la codificación de strings"""
    print("\n=== Prueba de Codificación de Strings ===")
    
    protocol = Protocol()
    
    test_strings = [
        "Hola",
        "Mundo",
        "Test con espacios",
        "Test con ñ y áéíóú",
        "",  # string vacío
        "A" * 1000  # string largo
    ]
    
    for test_str in test_strings:
        encoded = protocol._encode_string(test_str)
        decoded, _ = protocol._decode_string(encoded, 0)
        
        if decoded == test_str:
            print(f"✅ '{test_str}' -> {len(encoded)} bytes")
        else:
            print(f"❌ Error: '{test_str}' != '{decoded}'")
            return False
    
    return True

def test_error_handling():
    """Prueba el manejo de errores"""
    print("\n=== Prueba de Manejo de Errores ===")
    
    protocol = Protocol()
    
    # Prueba con datos incompletos
    try:
        protocol._decode_string(b"", 0)
        print("❌ Debería haber fallado con datos vacíos")
        return False
    except ValueError:
        print("✅ Correctamente detecta datos insuficientes")
    
    # Prueba con longitud inválida
    try:
        protocol._decode_string(b"\x00\x01", 0)
        print("❌ Debería haber fallado con longitud inválida")
        return False
    except ValueError:
        print("✅ Correctamente detecta longitud inválida")
    
    return True

def test_protocol_constants():
    """Prueba las constantes del protocolo"""
    print("\n=== Prueba de Constantes del Protocolo ===")
    
    # Verificar constantes
    assert Protocol.DELIMITER == b'\xFF'
    assert Protocol.HEADER_SIZE == 5
    assert Protocol.MAX_MESSAGE_SIZE == 8192
    
    # Verificar tipos de mensaje
    assert Protocol.MSG_BET == 0x01
    assert Protocol.MSG_SUCCESS == 0x03
    assert Protocol.MSG_ERROR == 0x04
    
    print("✅ Todas las constantes son correctas")
    return True

def main():
    """Función principal de pruebas"""
    print("Iniciando pruebas del protocolo de comunicación...")
    
    tests = [
        test_protocol_constants,
        test_string_encoding,
        test_message_structure,
        test_protocol_encoding,
        test_error_handling,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} falló")
        except Exception as e:
            print(f"❌ Test {test.__name__} falló con excepción: {e}")
    
    print(f"\n=== Resultados ===")
    print(f"Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        return 0
    else:
        print("❌ Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit(main())
