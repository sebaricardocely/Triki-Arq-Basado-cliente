import socket
import threading
import tkinter as tk
from tkinter import messagebox

class TrikiClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window = tk.Tk()
        self.window.title("Triki")
        self.buttons = []
        self.create_board()
        self.start_client()

    def create_board(self):
        for i in range(9):
            button = tk.Button(self.window, text=' ', font=('Arial', 24), width=5, height=2,
                               command=lambda i=i: self.send_move(i), bg='lightgrey')
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

    def start_client(self):
        self.client_socket.connect(('localhost', 12345))  # Conectar al servidor
        threading.Thread(target=self.receive_messages, daemon=True).start()  # Hilo para recibir mensajes

    def send_move(self, move):
        if self.buttons[move]['text'] == ' ':  # Comprobar si la casilla está vacía
            self.client_socket.send(str(move).encode())  # Enviar movimiento al servidor

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()  # Recibir mensajes del servidor
                if not message:
                    break
                self.handle_message(message)
            except Exception as e:
                print(f"Error al recibir mensaje: {e}")  # Imprimir error
                break
        self.client_socket.close()  # Cerrar el socket

    def handle_message(self, message):
        if "ha ganado" in message or "Es un empate" in message:
            messagebox.showinfo("Resultado", message)  # Mostrar mensaje de resultado
            self.reset_board()  # Reiniciar el tablero
        else:
            self.update_board(message)  # Actualizar el tablero

    def update_board(self, board_str):
        board = board_str.split('\n')
        for i, row in enumerate(board):
            cells = row.split('|')
            for j, cell in enumerate(cells):
                if cell == 'X':
                    self.buttons[i * 3 + j]['text'] = cell  # Actualizar el texto del botón
                    self.buttons[i * 3 + j]['fg'] = 'red'  # Color para X
                elif cell == 'O':
                    self.buttons[i * 3 + j]['text'] = cell  # Actualizar el texto del botón
                    self.buttons[i * 3 + j]['fg'] = 'blue'  # Color para O
                else:
                    self.buttons[i * 3 + j]['text'] = ' '  # Reiniciar casillas vacías

    def reset_board(self):
        for button in self.buttons:
            button['text'] = ' '  # Reiniciar el tablero
            button['fg'] = 'black'  # Reiniciar el color

if __name__ == "__main__":
    client = TrikiClient()
    client.window.mainloop()  # Iniciar el bucle principal de la interfaz
