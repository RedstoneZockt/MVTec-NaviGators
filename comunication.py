import socket

class Transceiver:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


    def send_data(self, data):
        # Create a new socket for each connection attempt
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((self.ip, self.port))  # Connect to the server
            client.sendall(data.encode())  # Send data
        except ConnectionRefusedError:
            print("Error: Could not connect to server. Make sure the server is running.")
        finally:
            client.close()  # Close the socket after sending the message
