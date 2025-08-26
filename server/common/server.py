import socket
import logging
import signal
import sys
import threading
from protocol import Protocol


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
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle SIGTERM and SIGINT signals for graceful shutdown"""
        logging.info(f'action: signal_received | result: success | signal: {signum}')
        self._shutdown_requested = True
        self._graceful_shutdown()

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
        Process bet from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        # Add connection to active list
        with self._connections_lock:
            self._active_connections.append(client_sock)
        
        try:
            # Process bet using protocol
            success = self._protocol.process_bet(client_sock)
            addr = client_sock.getpeername()
            if success:
                logging.info(f'action: bet_processed | result: success | ip: {addr[0]}')
            else:
                logging.error(f'action: bet_processed | result: fail | ip: {addr[0]}')
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
