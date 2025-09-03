import logging
import socket
import struct
from typing import Optional, Tuple, List
from .utils import Bet, store_bets

class Protocol:    
    DELIMITER = b'\xFF'
    HEADER_SIZE = 5  # 4 bytes longitud + 1 byte tipo
    MAX_MESSAGE_SIZE = 8192  # 8KB máximo
    
    MSG_BET = 0x01
    MSG_BATCH = 0x02
    MSG_SUCCESS = 0x03
    MSG_ERROR = 0x04
    MSG_FINISHED = 0x05
    MSG_WINNERS_QUERY = 0x06
    MSG_WINNERS_RESPONSE = 0x07

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
            agency, offset = self._decode_string(payload, offset)
            nombre, offset = self._decode_string(payload, offset)
            apellido, offset = self._decode_string(payload, offset)
            dni, offset = self._decode_string(payload, offset)
            nacimiento, offset = self._decode_string(payload, offset)
            numero, offset = self._decode_string(payload, offset)
            
            # Crear objeto Bet
            bet = Bet(
                agency=agency,
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
        payload += self._encode_string(str(bet.agency))
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
    
    def decode_batch(self, payload: bytes) -> Optional[List[Bet]]:
        """
        Decodifica un batch de apuestas desde el payload
        """
        try:
            offset = 0
            
            # Leer cantidad de apuestas (4 bytes)
            if offset + 4 > len(payload):
                raise ValueError("Datos insuficientes para decodificar cantidad")
            
            cantidad = struct.unpack('!I', payload[offset:offset+4])[0]
            offset += 4
            
            bets = []
            for _ in range(cantidad):
                # Leer longitud de la apuesta (4 bytes)
                if offset + 4 > len(payload):
                    raise ValueError("Datos insuficientes para decodificar longitud de apuesta")
                
                bet_length = struct.unpack('!I', payload[offset:offset+4])[0]
                offset += 4
                
                # Leer apuesta
                if offset + bet_length > len(payload):
                    raise ValueError("Datos insuficientes para decodificar apuesta")
                
                bet_data = payload[offset:offset+bet_length]
                bet = self.decode_bet(bet_data)
                if not bet:
                    raise ValueError("Error decodificando apuesta individual")
                
                bets.append(bet)
                offset += bet_length
            
            return bets
            
        except Exception as e:
            logging.error(f"action: decode_batch | result: fail | error: {e}")
            return None
    
    def receive_batch(self, client_sock: socket.socket) -> Optional[List[Bet]]:
        """
        Recibe un batch de apuestas del cliente
        """
        result = self.receive_message(client_sock)
        if not result:
            return None
        
        msg_type, payload = result
        
        if msg_type != self.MSG_BATCH:
            logging.error(f"action: receive_batch | result: fail | error: unexpected message type {msg_type}")
            return None
        
        return self.decode_batch(payload)
    
    def process_batch(self, client_sock: socket.socket) -> bool:
        """
        Procesa un batch de apuestas: recibe, almacena todas y responde
        """
        # Recibir batch de apuestas
        bets = self.receive_batch(client_sock)
        if not bets:
            return False
        
        cantidad = len(bets)
        success = True
        
        try:
            # Almacenar todas las apuestas
            try:
                store_bets(bets)
                for bet in bets:
                    logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            except Exception as e:
                logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
                success = False
            
            # Log del resultado del batch
            if success:
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {cantidad}")
            else:
                logging.error(f"action: apuesta_recibida | result: fail | cantidad: {cantidad}")
            
            # Enviar respuesta de confirmación (usamos la primera apuesta como referencia)
            first_bet = bets[0]
            return self.send_response(client_sock, success, first_bet.document, str(first_bet.number))
            
        except Exception as e:
            logging.error(f"action: process_batch | result: fail | error: {e}")
            # Enviar respuesta de error
            first_bet = bets[0] if bets else None
            if first_bet:
                self.send_response(client_sock, False, first_bet.document, str(first_bet.number))
            return False
    
    def process_message(self, client_sock: socket.socket) -> bool:
        """
        Procesa un mensaje (apuesta individual o batch) y determina el tipo automáticamente
        """
        # Recibir mensaje para determinar el tipo
        result = self.receive_message(client_sock)
        if not result:
            return False
        
        msg_type, payload = result
        
        if msg_type == self.MSG_BATCH:
            return self._process_batch_from_payload(client_sock, payload)
        elif msg_type == self.MSG_BET:
            return self._process_bet_from_payload(client_sock, payload)
        else:
            logging.error(f"action: process_message | result: fail | error: unknown message type {msg_type}")
            return False
    
    def _process_bet_from_payload(self, client_sock: socket.socket, payload: bytes) -> bool:
        """
        Procesa una apuesta individual desde el payload ya recibido
        """
        bet = self.decode_bet(payload)
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
    
    def _process_batch_from_payload(self, client_sock: socket.socket, payload: bytes) -> bool:
        """
        Procesa un batch de apuestas desde el payload ya recibido
        """
        bets = self.decode_batch(payload)
        if not bets:
            return False
        
        cantidad = len(bets)
        success = True
        
        try:
            # Almacenar todas las apuestas
            try:
                store_bets(bets)
                for bet in bets:
                    logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            except Exception as e:
                logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
                success = False
            
            # Log del resultado del batch
            if success:
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {cantidad}")
            else:
                logging.error(f"action: apuesta_recibida | result: fail | cantidad: {cantidad}")
            
            # Enviar respuesta de confirmación (usamos la primera apuesta como referencia)
            first_bet = bets[0]
            return self.send_response(client_sock, success, first_bet.document, str(first_bet.number))
            
        except Exception as e:
            logging.error(f"action: process_batch | result: fail | error: {e}")
            # Enviar respuesta de error
            first_bet = bets[0] if bets else None
            if first_bet:
                self.send_response(client_sock, False, first_bet.document, str(first_bet.number))
            return False
    
    def receive_finished_notification(self, client_sock: socket.socket) -> Optional[str]:
        """
        Recibe notificación de finalización de una agencia
        """
        result = self.receive_message(client_sock)
        if not result:
            return None
        
        msg_type, payload = result
        
        if msg_type != self.MSG_FINISHED:
            logging.error(f"action: receive_finished | result: fail | error: unexpected message type {msg_type}")
            return None
        
        try:
            offset = 0
            agency_id, _ = self._decode_string(payload, offset)
            return agency_id
        except Exception as e:
            logging.error(f"action: receive_finished | result: fail | error: {e}")
            return None
    
    def send_finished_ack(self, client_sock: socket.socket, success: bool) -> bool:
        """
        Envía confirmación de recepción de notificación de finalización
        """
        msg_type = self.MSG_SUCCESS if success else self.MSG_ERROR
        payload = self._encode_string("OK" if success else "ERROR")
        return self.send_message(client_sock, msg_type, payload)
    
    def receive_winners_query(self, client_sock: socket.socket) -> Optional[str]:
        """
        Recibe consulta de ganadores de una agencia
        """
        result = self.receive_message(client_sock)
        if not result:
            return None
        
        msg_type, payload = result
        
        if msg_type != self.MSG_WINNERS_QUERY:
            logging.error(f"action: receive_winners_query | result: fail | error: unexpected message type {msg_type}")
            return None
        
        try:
            offset = 0
            agency_id, _ = self._decode_string(payload, offset)
            return agency_id
        except Exception as e:
            logging.error(f"action: receive_winners_query | result: fail | error: {e}")
            return None
    
    def send_winners_response(self, client_sock: socket.socket, winners: list[str]) -> bool:
        """
        Envía respuesta con la lista de ganadores
        """
        payload = b""
        
        # Escribir cantidad de ganadores (4 bytes)
        payload += struct.pack('!I', len(winners))
        
        # Escribir cada DNI ganador
        for winner in winners:
            payload += self._encode_string(winner)
        
        return self.send_message(client_sock, self.MSG_WINNERS_RESPONSE, payload)
    
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
