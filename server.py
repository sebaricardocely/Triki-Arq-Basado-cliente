import socket
import threading

class TrikiServer:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # Tablero vacío
        self.current_player = 'X'  # Jugador actual
        self.clients = []  # Lista de clientes conectados
        self.lock = threading.Lock()  # Bloqueo para manejar accesos concurrentes

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 12345))  # Vincular el socket a una dirección y puerto
        server_socket.listen(2)  # Esperar hasta 2 conexiones
        print("Servidor iniciado. Esperando jugadores...")

        while len(self.clients) < 2:  # Aceptar 2 jugadores
            client_socket, addr = server_socket.accept()  # Aceptar conexión
            self.clients.append(client_socket)  # Agregar cliente a la lista
            print(f"Jugador conectado desde {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()  # Manejar el cliente en un nuevo hilo

        print("Ambos jugadores conectados. ¡Comienza el juego!")
        self.send_board()  # Enviar el tablero inicial

    def handle_client(self, client_socket):
        while True:
            try:
                move = client_socket.recv(1024).decode()  # Recibir el movimiento del cliente
                if not move:
                    break
                self.make_move(move, client_socket)  # Procesar el movimiento
            except Exception as e:
                print(f"Error al manejar el cliente: {e}")  # Imprimir error
                break
        client_socket.close()  # Cerrar el socket del cliente

    def make_move(self, move, client_socket):
        move = int(move)  # Convertir el movimiento a entero
        if self.board[move] == ' ':  # Verificar si la posición está vacía
            self.board[move] = self.current_player  # Colocar la marca del jugador
            winner = None
            if self.check_winner():  # Verificar si hay un ganador
                winner = self.current_player
                self.send_board()  # Enviar el tablero final
                self.broadcast(f"¡Jugador {'1' if winner == 'X' else '2'} es el ganador!")  # Anunciar el ganador
                self.reset_game()  # Reiniciar el juego
            elif ' ' not in self.board:  # Verificar empate
                self.send_board()
                self.broadcast("¡Es un empate!")  # Anunciar empate
                self.reset_game()  # Reiniciar el juego
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'  # Cambiar al siguiente jugador
                self.send_board()  # Enviar el tablero actualizado
                self.broadcast(f"Turno del jugador {'1' if self.current_player == 'X' else '2'}")  # Anunciar turno

    def send_board(self):
        # Crear una representación del tablero
        board_str = '\n'.join(['|'.join(self.board[i:i + 3]) for i in range(0, 9, 3)])
        self.broadcast(board_str)  # Enviar el tablero a todos los jugadores

    def broadcast(self, message):
        with self.lock:
            for client in self.clients:
                client.send(message.encode())  # Enviar mensaje a cada cliente

    def check_winner(self):
        # Comprobación de las combinaciones ganadoras
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]               # Diagonales
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return True
        return False

    def reset_game(self):
        self.board = [' ' for _ in range(9)]  # Reiniciar el tablero
        self.current_player = 'X'  # Reiniciar el jugador
        self.clients = []  # Reiniciar la lista de clientes


if __name__ == "__main__":
    server = TrikiServer()
    server.start_server()
