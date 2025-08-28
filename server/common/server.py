import socket
import logging
import signal
import sys
import threading
from .protocol import Protocol


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        
        # Flag to control graceful shutdown
        self._shutdown_requested = False
        self._active_connections = []
        self._connections_lock = threading.Lock()
        
        # Protocol for handling bets
        self._protocol = Protocol()
        
        # State for tracking finished agencies and lottery status
        self._finished_agencies = set()
        self._lottery_completed = False
        self._state_lock = threading.Lock()
        
        # Limpiar archivo de apuestas al iniciar el servidor
        self._clear_bets_file()
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle SIGTERM and SIGINT signals for graceful shutdown"""
        logging.info(f'action: signal_received | result: success | signal: {signum}')
        self._shutdown_requested = True
        self._graceful_shutdown()

    def _mark_agency_finished(self, agency_id: str) -> bool:
        """Marca una agencia como finalizada y verifica si todas terminaron"""
        with self._state_lock:
            self._finished_agencies.add(agency_id)
            logging.info(f'action: agency_finished | result: success | agency: {agency_id}')
            
            # Verificar si todas las 5 agencias terminaron
            if len(self._finished_agencies) == 5 and not self._lottery_completed:
                self._lottery_completed = True
                logging.info('action: sorteo | result: success')
                return True
            return False
    
    def _clear_bets_file(self):
        """Limpia el archivo de apuestas al iniciar el servidor"""
        try:
            from .utils import STORAGE_FILEPATH
            # Crear archivo vacío
            with open(STORAGE_FILEPATH, 'w') as file:
                pass  # Crear archivo vacío
            logging.info(f'action: clear_bets_file | result: success')
        except Exception as e:
            logging.error(f'action: clear_bets_file | result: fail | error: {e}')
    
    def _get_winners_for_agency(self, agency_id: str) -> list[str]:
        """Obtiene los ganadores de una agencia específica"""
        try:
            from .utils import load_bets, has_won
            
            winners = []
            # load_bets() es un generador, necesitamos iterarlo
            for bet in load_bets():
                if str(bet.agency) == agency_id and has_won(bet):
                    winners.append(bet.document)
            
            return winners
        except Exception as e:
            logging.error(f'action: get_winners | result: fail | agency: {agency_id} | error: {e}')
            return []
    
    def _graceful_shutdown(self):
        """Perform graceful shutdown of all resources"""
        logging.info('action: graceful_shutdown | result: in_progress')
        
        # Close all active client connections
        with self._connections_lock:
            for client_sock in self._active_connections:
                try:
                    logging.info('action: close_client_connection | result: in_progress')
                    client_sock.close()
                    logging.info('action: close_client_connection | result: success')
                except Exception as e:
                    logging.error(f'action: close_client_connection | result: fail | error: {e}')
        
        # Close server socket
        try:
            logging.info('action: close_server_socket | result: in_progress')
            self._server_socket.close()
            logging.info('action: close_server_socket | result: success')
        except Exception as e:
            logging.error(f'action: close_server_socket | result: fail | error: {e}')
        
        logging.info('action: graceful_shutdown | result: success')
        sys.exit(0)

    def run(self):
        """
        Server loop with graceful shutdown support

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        logging.info('action: server_start | result: success')
        
        while not self._shutdown_requested:
            try:
                # Set a timeout on accept to allow checking shutdown flag
                self._server_socket.settimeout(1.0)
                client_sock = self.__accept_new_connection()
                if client_sock:
                    self.__handle_client_connection(client_sock)
            except socket.timeout:
                # Timeout occurred, check if shutdown was requested
                continue
            except Exception as e:
                if not self._shutdown_requested:
                    logging.error(f'action: accept_connection | result: fail | error: {e}')
                break
        
        # If we get here, shutdown was requested
        self._graceful_shutdown()

    def __handle_client_connection(self, client_sock):
        """
        Process multiple messages from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        # Add connection to active list
        with self._connections_lock:
            self._active_connections.append(client_sock)
        
        try:
            addr = client_sock.getpeername()
            # Process multiple messages until connection is closed or error occurs
            while True:
                try:
                    # Receive message to determine type
                    result = self._protocol.receive_message(client_sock)
                    if not result:
                        logging.info(f'action: client_disconnected | result: success | ip: {addr[0]}')
                        break
                    
                    msg_type, payload = result
                    
                    # Process different message types
                    if msg_type == self._protocol.MSG_BET:
                        success = self._protocol._process_bet_from_payload(client_sock, payload)
                        if success:
                            logging.info(f'action: bet_processed | result: success | ip: {addr[0]}')
                        else:
                            logging.error(f'action: bet_processed | result: fail | ip: {addr[0]}')
                            break
                    
                    elif msg_type == self._protocol.MSG_BATCH:
                        success = self._protocol._process_batch_from_payload(client_sock, payload)
                        if success:
                            logging.info(f'action: batch_processed | result: success | ip: {addr[0]}')
                        else:
                            logging.error(f'action: batch_processed | result: fail | ip: {addr[0]}')
                            break
                    
                    elif msg_type == self._protocol.MSG_FINISHED:
                        # Handle finished notification
                        try:
                            offset = 0
                            agency_id, _ = self._protocol._decode_string(payload, offset)
                            # Mark agency as finished
                            lottery_completed = self._mark_agency_finished(agency_id)
                            # Send acknowledgment
                            self._protocol.send_finished_ack(client_sock, True)
                            logging.info(f'action: finished_notification | result: success | agency: {agency_id}')
                        except Exception as e:
                            self._protocol.send_finished_ack(client_sock, False)
                            logging.error(f'action: finished_notification | result: fail | ip: {addr[0]} | error: {e}')
                            break
                    
                    elif msg_type == self._protocol.MSG_WINNERS_QUERY:
                        # Handle winners query
                        try:
                            offset = 0
                            agency_id, _ = self._protocol._decode_string(payload, offset)
                            # Check if lottery is completed
                            with self._state_lock:
                                if not self._lottery_completed:
                                    # Lottery not completed yet, send empty response
                                    self._protocol.send_winners_response(client_sock, [])
                                    logging.warning(f'action: winners_query | result: pending | agency: {agency_id}')
                                else:
                                    # Get winners for this agency
                                    winners = self._get_winners_for_agency(agency_id)
                                    self._protocol.send_winners_response(client_sock, winners)
                                    logging.info(f'action: winners_query | result: success | agency: {agency_id} | winners: {len(winners)}')
                        except Exception as e:
                            logging.error(f'action: winners_query | result: fail | ip: {addr[0]} | error: {e}')
                            break
                    
                    else:
                        logging.error(f'action: unknown_message | result: fail | type: {msg_type} | ip: {addr[0]}')
                        break
                        
                except (OSError, ConnectionResetError, BrokenPipeError) as e:
                    # Connection was closed by client or network error
                    logging.info(f'action: client_disconnected | result: success | ip: {addr[0]}')
                    break
                except Exception as e:
                    # Check if it's a connection closed error from receive_message
                    if "connection closed" in str(e).lower():
                        logging.info(f'action: client_disconnected | result: success | ip: {addr[0]}')
                        break
                    logging.error(f"action: message_processed | result: fail | error: {e}")
                    break
        except OSError as e:
            logging.error(f"action: bet_processed | result: fail | error: {e}")
        finally:
            # Remove connection from active list and close
            with self._connections_lock:
                if client_sock in self._active_connections:
                    self._active_connections.remove(client_sock)
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
