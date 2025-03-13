import socket

while True:
    user_input = input("Enter something: ")
    print("You entered:", user_input)

    # Create a new socket for each connection attempt
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(("127.0.0.1", 6000))  # Connect to the server
        client.sendall(user_input.encode())  # Send data
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Make sure the server is running.")
    finally:
        client.close()  # Close the socket after sending the message
