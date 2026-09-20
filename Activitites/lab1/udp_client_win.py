import socket

# Reemplaza con la dirección IP de tu servidor Linux
SERVER_IP = "192.168.80.24"  
SERVER_PORT = 65433

def main():
    try:
        # Creación del socket UDP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            # Tiempo de espera máximo de 3 segundos para evitar que se quede colgado si no responde el servidor
            client_socket.settimeout(3.0)
            
            mensaje = "Hola Servidor Linux, saludo desde Windows (UDP)"
            print(f"[UDP] Enviando datagrama a {SERVER_IP}:{SERVER_PORT}...")
            client_socket.sendto(mensaje.encode('utf-8'), (SERVER_IP, SERVER_PORT))
            
            # Recepción de la respuesta
            respuesta, addr = client_socket.recvfrom(1024)
            print(f"[UDP] Respuesta desde {addr}: {respuesta.decode('utf-8')}")
            
    except socket.timeout:
        print("[UDP] Tiempo de espera agotado (Timeout). El servidor no respondió o el puerto está cerrado/bloqueado.")
    except Exception as e:
        print(f"[ERROR] Ocurrió un fallo: {e}")

if __name__ == "__main__":
    main()