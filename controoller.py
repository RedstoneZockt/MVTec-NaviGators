import socket
#import serial
import time

from can.interfaces import serial


# MODE:
# 1 - Forward, Backward, Turn left, Turn right control
# 2 - To goal controller
# 3 - To goal controller with obstacles collision avoid

# Socket communication for parts of the code
class Communication():
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(1)
        self.controller = Controller()

    def listen(self):
        conn, addr = self.server.accept()
        data = conn.recv(1024)
        conn.close()
        return data.decode()

    def data_recognition_controller(self, data):
        try:
            if data[0] == "M":
                self.controller.set_mode(int(data[1]))
            elif data[0] == "F":
                self.controller.go_forward()
            elif data[0] == "B":
                self.controller.go_back()
            elif data[0] == "R":
                self.controller.go_right()
            elif data[0] == "L":
                self.controller.go_left()
            elif data[0] == "S":
                if (len(data) == 1):
                    self.controller.go_stop()
                else:
                    self.controller.set_speed(int(data[1:4]))
            else:
                print("Unknown command")
        except:
            print("Message error:", data)




class Controller():
    def __init__(self):
        self.mode = 1
        # Goal [x, y]
        self.goal = [0, 0]

        # Actual position [x, y]
        self.actual_position = [0, 0]

        # Speed
        self.speed = 0

        #serial
        self.serial = SerialCommunication("/dev/ttyUSB0")

        self.right_speed = 0
        self.left_speed = 0

    def set_mode(self, mode):
        self.mode = mode
        print("Mode changed to ", mode)

    def set_speed(self, speed):
        self.speed = speed
        print("Speed changed to ", speed)

    def go_forward(self):
        self.set_right_side(self.speed)
        self.set_left_side(self.speed)

    def go_back(self):
        self.set_right_side(-self.speed)
        self.set_left_side(-self.speed)

    def go_right(self):
        self.set_right_side(self.speed)
        self.set_left_side(-self.speed)

    def go_left(self):
        self.set_right_side(-self.speed)
        self.set_left_side(self.speed)

    def go_stop(self):
        self.set_right_side(0.0)
        self.set_left_side(0.0)


    # Right side control
    def set_right_side(self, speed):
        self.left_speed = self.speed_normalize_funcion(speed)

    # Left side control
    def set_left_side(self, speed):
        self.right_speed = self.speed_normalize_funcion(speed)

    def speed_normalize_funcion(self, speed):
        in_min = -100
        in_max = 100
        out_min = 0
        out_max = 512
        return (speed - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def controller_data_sender(self):
        self.serial.send_data(":ML=" + str(self.left_speed) + "!")
        self.serial.send_data(":MR=" + str(self.right_speed) + "!")


class SerialCommunication():
    def __init__(self, port):
        self.serial = serial.Serial(port)
        self.heart_beat = True

    def send_data(self, data):
        command_heart_beat: str = ":WD=" + str(int(self.heart_beat)) + "!"
        self.serial.write(command_heart_beat.encode())
        serial.write(data.encode())
        self.heart_beat = not self.heart_beat

communication = Communication("127.0.0.1", 6000)

while True:
    data = communication.listen()
    communication.data_recognition_controller(data)
    communication.controller.controller_data_sender()




