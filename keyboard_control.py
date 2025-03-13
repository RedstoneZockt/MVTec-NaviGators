import keyboard
import comunication


speed = 50

print("Press W/A/S/D to move, Q to quit.")


communication = comunication.Transceiver('127.0.0.1', 6000)
communication.send_data('S' + str(speed))

while True:
    # Forward
    if keyboard.is_pressed("w"):
        communication.send_data('F')

    # Backward
    elif keyboard.is_pressed("s"):
        communication.send_data('B')

    # Left
    elif keyboard.is_pressed("a"):
        communication.send_data('L')

    # Right
    elif keyboard.is_pressed("d"):
        communication.send_data('R')

    # Quit
    elif keyboard.is_pressed("q"):
        communication.send_data('S')
        print("Exiting...")
        break
    # Stop
    else:
        communication.send_data('S')
