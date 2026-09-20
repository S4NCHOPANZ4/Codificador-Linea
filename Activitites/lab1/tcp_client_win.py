import socket

SERVER_IP = "192.168.80.24"  
SERVER_PORT = 65432

def main():
    try:
        # Creación del socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"[TCP] Conectando a {SERVER_IP}:{SERVER_PORT}...")
            client_socket.connect((SERVER_IP, SERVER_PORT))
            
            mensaje = "Hola Servidor Linux, saludo desde Windows (TCP)"
            print(f"[TCP] Enviando: {mensaje}")
            client_socket.sendall(mensaje.encode('utf-8'))
            
            # Recepción de la respuesta
            respuesta = client_socket.recv(1024)
            print(f"[TCP] Respuesta recibida: {respuesta.decode('utf-8')}")
            
    except ConnectionRefusedError:
        print("[ERROR] Conexión rechazada. Asegúrate de que el servidor TCP esté corriendo en Linux y el puerto esté abierto.")
    except Exception as e:
        print(f"[ERROR] Ocurrió un fallo: {e}")

if __name__ == "__main__":
    main()