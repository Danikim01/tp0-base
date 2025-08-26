import json
import logging
import socket
from typing import Optional, Tuple
from .utils import Bet, store_bet

class Protocol:
    """Maneja la comunicación entre cliente y servidor"""
    
    def __init__(self):
        pass
    
    def receive_bet(self, client_sock: socket.socket) -> Optional[Bet]:
        """
        Recibe una apuesta del cliente evitando short-read
        """
        try:
            # Leer hasta el delimitador de línea
            data = b""
            while not data.endswith(b'\n'):
                chunk = client_sock.recv(1024)
                if not chunk:
                    logging.error("action: receive_bet | result: fail | error: connection closed")
                    return None
                data += chunk
            
            # Decodificar y parsear JSON
            message = data.decode('utf-8').strip()
            request = json.loads(message)
            
            if request.get('type') != 'bet':
                logging.error("action: receive_bet | result: fail | error: invalid message type")
                return None
            
            bet_data = request.get('bet', {})
            
            # Validar que todos los campos estén presentes
            required_fields = ['nombre', 'apellido', 'dni', 'nacimiento', 'numero']
            for field in required_fields:
                if not bet_data.get(field):
                    logging.error(f"action: receive_bet | result: fail | error: missing field {field}")
                    return None
            
            # Crear objeto Bet
            bet = Bet(
                agency=1,  # Por defecto, se puede modificar según necesidades
                first_name=bet_data.get('nombre', ''),
                last_name=bet_data.get('apellido', ''),
                document=bet_data.get('dni', ''),
                birthdate=bet_data.get('nacimiento', ''),
                number=bet_data.get('numero', '')
            )
            
            return bet
            
        except json.JSONDecodeError as e:
            logging.error(f"action: receive_bet | result: fail | error: invalid JSON - {e}")
            return None
        except Exception as e:
            logging.error(f"action: receive_bet | result: fail | error: {e}")
            return None
    
    def send_response(self, client_sock: socket.socket, status: str, dni: str, numero: str) -> bool:
        """
        Envía respuesta al cliente evitando short-write
        """
        try:
            response = {
                'type': 'bet_response',
                'status': status,
                'dni': dni,
                'numero': numero
            }
            
            data = json.dumps(response) + '\n'
            message = data.encode('utf-8')
            
            # Enviar datos completos evitando short-write
            total_sent = 0
            while total_sent < len(message):
                sent = client_sock.send(message[total_sent:])
                if sent == 0:
                    logging.error("action: send_response | result: fail | error: connection broken")
                    return False
                total_sent += sent
            
            return True
            
        except Exception as e:
            logging.error(f"action: send_response | result: fail | error: {e}")
            return False
    
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
            store_bet(bet)
            
            # Log de confirmación según formato requerido
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            
            # Enviar respuesta de confirmación
            return self.send_response(client_sock, "success", bet.document, str(bet.number))
            
        except Exception as e:
            logging.error(f"action: process_bet | result: fail | error: {e}")
            # Enviar respuesta de error
            self.send_response(client_sock, "error", bet.document, str(bet.number))
            return False
