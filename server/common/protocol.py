import logging
import socket
import struct
from typing import Optional, Tuple, List
from .utils import Bet, store_bets

class Protocol:
    """Protocolo de comunicación propio sin JSON"""
    
    # Constantes del protocolo
    DELIMITER = b'\xFF'
    HEADER_SIZE = 5  # 4 bytes longitud + 1 byte tipo
    MAX_MESSAGE_SIZE = 8192  # 8KB máximo
    
    # Tipos de mensaje
    MSG_BET = 0x01
    MSG_SUCCESS = 0x03
    MSG_ERROR = 0x04

    def __init__(self):
        pass
    
    def _read_exact(self, sock: socket.socket, size: int) -> Optional[bytes]:
        """Lee exactamente 'size' bytes del socket"""
        data = b""
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _write_exact(self, sock: socket.socket, data: bytes) -> bool:
        """Escribe exactamente todos los datos al socket"""
        total_sent = 0
        while total_sent < len(data):
            sent = sock.send(data[total_sent:])
            if sent == 0:
                return False
            total_sent += sent
        return True
    
    def _encode_string(self, s: str) -> bytes:
        """Codifica una string con su longitud"""
        encoded = s.encode('utf-8')
        return struct.pack('!H', len(encoded)) + encoded
    
    def _decode_string(self, data: bytes, offset: int) -> Tuple[str, int]:
        """Decodifica una string con su longitud"""
        if offset + 2 > len(data):
            raise ValueError("Datos insuficientes para decodificar string")
        
        length = struct.unpack('!H', data[offset:offset+2])[0]
        offset += 2
        
        if offset + length > len(data):
            raise ValueError("Datos insuficientes para decodificar string")
        
        string_data = data[offset:offset+length]
        return string_data.decode('utf-8'), offset + length
    
    def receive_message(self, client_sock: socket.socket) -> Optional[Tuple[int, bytes]]:
        """
        Recibe un mensaje completo del cliente
        Retorna: (tipo_mensaje, payload) o None si hay error
        """
        try:
            # Leer header (longitud + tipo)
            header = self._read_exact(client_sock, self.HEADER_SIZE)
            if not header:
                logging.error("action: receive_message | result: fail | error: connection closed")
                return None
            
            # Parsear header
            payload_length, msg_type = struct.unpack('!IB', header)
            
            # Validar longitud
            if payload_length > self.MAX_MESSAGE_SIZE:
                logging.error(f"action: receive_message | result: fail | error: message too large ({payload_length} bytes)")
                return None
            
            # Leer payload
            payload = self._read_exact(client_sock, payload_length)
            if not payload:
                logging.error("action: receive_message | result: fail | error: incomplete payload")
                return None
            
            # Leer delimitador
            delimiter = self._read_exact(client_sock, 1)
            if not delimiter or delimiter != self.DELIMITER:
                logging.error("action: receive_message | result: fail | error: invalid delimiter")
                return None
            
            return msg_type, payload
            
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None
    
    def send_message(self, client_sock: socket.socket, msg_type: int, payload: bytes) -> bool:
        """
        Envía un mensaje completo al cliente
        """
        try:
            # Construir mensaje completo
            header = struct.pack('!IB', len(payload), msg_type)
            message = header + payload + self.DELIMITER
            
            # Enviar mensaje completo
            return self._write_exact(client_sock, message)
            
        except Exception as e:
            logging.error(f"action: send_message | result: fail | error: {e}")
            return False
    
    def decode_bet(self, payload: bytes) -> Optional[Bet]:
        """
        Decodifica una apuesta desde el payload
        """
        try:
            offset = 0
            
            # Decodificar campos
            nombre, offset = self._decode_string(payload, offset)
            apellido, offset = self._decode_string(payload, offset)
            dni, offset = self._decode_string(payload, offset)
            nacimiento, offset = self._decode_string(payload, offset)
            numero, offset = self._decode_string(payload, offset)
            
            # Crear objeto Bet
            bet = Bet(
                agency="1",  # Por defecto
                first_name=nombre,
                last_name=apellido,
                document=dni,
                birthdate=nacimiento,
                number=numero
            )
            
            return bet
            
        except Exception as e:
            logging.error(f"action: decode_bet | result: fail | error: {e}")
            return None
    
    def encode_bet(self, bet: Bet) -> bytes:
        """
        Codifica una apuesta a bytes
        """
        payload = b""
        payload += self._encode_string(bet.first_name)
        payload += self._encode_string(bet.last_name)
        payload += self._encode_string(bet.document)
        # Convertir datetime.date a string ISO format
        birthdate_str = bet.birthdate.isoformat()
        payload += self._encode_string(birthdate_str)
        payload += self._encode_string(str(bet.number))
        return payload
    
    def encode_response(self, dni: str, numero: str) -> bytes:
        """
        Codifica una respuesta a bytes
        """
        payload = b""
        payload += self._encode_string(dni)
        payload += self._encode_string(numero)
        return payload
    
    def receive_bet(self, client_sock: socket.socket) -> Optional[Bet]:
        """
        Recibe una apuesta del cliente
        """
        result = self.receive_message(client_sock)
        if not result:
            return None
        
        msg_type, payload = result
        
        if msg_type != self.MSG_BET:
            logging.error(f"action: receive_bet | result: fail | error: unexpected message type {msg_type}")
            return None
        
        return self.decode_bet(payload)
    
    def send_response(self, client_sock: socket.socket, success: bool, dni: str, numero: str) -> bool:
        """
        Envía respuesta al cliente
        """
        msg_type = self.MSG_SUCCESS if success else self.MSG_ERROR
        payload = self.encode_response(dni, numero)
        return self.send_message(client_sock, msg_type, payload)
    
    def process_bet(self, client_sock: socket.socket) -> bool:
        """
        Procesa una apuesta completa: recibe, almacena y responde
        """
        # Recibir apuesta
        bet = self.receive_bet(client_sock)
        if not bet:
            return False
        
        try:
            # Almacenar apuesta
            store_bets([bet])
            
            # Log de confirmación
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            
            # Enviar respuesta de confirmación
            return self.send_response(client_sock, True, bet.document, str(bet.number))
            
        except Exception as e:
            logging.error(f"action: process_bet | result: fail | error: {e}")
            # Enviar respuesta de error
            self.send_response(client_sock, False, bet.document, str(bet.number))
            return False
