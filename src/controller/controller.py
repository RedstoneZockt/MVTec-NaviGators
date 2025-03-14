import socket
#import serial
import time
import threading
import comunication
import odometry
import sys

serial_port = "/dev/ttyUSB0"
server_address = "127.0.0.1"
server_port = 3000
debug = True
# MODE:
# 1 - Forward, Backward, Turn left, Turn right control
# 2 - To goal controller
# 3 - To goal controller with obstacles collision avoid
# 4 - Follower
# 5 - Odometry test
# 6 - Differential Drive

class DifferentialController():
    def __init__(self):
        self.gain_linear = 10.0
        self.gain_angular = 10.0

        self.max_speed = 100.0

        self.distance = 0.0
        self.angle = 0.0

        self.right_chain_speed = 0.0
        self.left_chain_speed = 0.0

    def set_distance(self, distance):
        self.distance = distance/100
    def set_angle(self, angle):
        self.angle = angle/100

    def set_gain_linear(self, gain_linear):
        self.gain_linear = gain_linear/100
        print("Linear gain change: ", self.gain_linear)


    def set_gain_angular(self, gain_angular):
        self.gain_angular = gain_angular/100
        print("Angular gain change: ", self.gain_angular)

    def update(self):
        linear_velocity = self.gain_linear * self.distance
        if linear_velocity > self.max_speed:
            linear_velocity = self.max_speed
        elif linear_velocity < - self.max_speed:
            linear_velocity = -self.max_speed

        if self.angle > 0.0:
            self.right_chain_speed = linear_velocity - self.gain_angular * self.angle
            self.left_chain_speed = linear_velocity

        elif self.angle < 0.0:
            self.right_chain_speed = linear_velocity
            self.left_chain_speed = linear_velocity - self.gain_angular * self.angle

        else:
            self.right_chain_speed = linear_velocity
            self.left_chain_speed = linear_velocity

        print("Distance: " + str(self.distance))
        print("Angle: " + str(self.angle))
        print("Right chain: " + str(self.right_chain_speed))
        print("Light chain: " + str(self.left_chain_speed))
        print("Max speed: " + str(self.max_speed))




class FollowerController():
    def __init__(self):
        self.Kp = 1.0
        self.Ki = 0.0
        self.error = 0.0
        self.base_speed = 0.0

        self.right_chain_speed = 0.0
        self.left_chain_speed = 0.0

    def set_error(self, error):
        self.error = error

    def update(self):
        if self.error > 0.0:
            self.right_chain_speed = self.base_speed - self.Kp * self.error
            self.left_chain_speed = self.base_speed

        elif self.error < 0.0:
            self.right_chain_speed = self.base_speed
            self.left_chain_speed = self.base_speed - self.Kp * self.error

        else:
            self.right_chain_speed = self.base_speed
            self.left_chain_speed = self.base_speed






class Controller():
    def __init__(self, serial):
        self.mode = 1
        self.speed = 80
        self.serial = serial
        self.right_speed = self.speed_normalize_function(0)
        self.left_speed = self.speed_normalize_function(0)
        self.follower = FollowerController()
        self.differential = DifferentialController()
        self.odom = odometry.ChainDriveOdometry()
        self.left_speed_odom = 0
        self.right_speed_odom = 0


        self.running = True

    def __del__(self):
        self.running = False

    def differential_update(self):
        self.differential.update()
        self.set_left_side(self.differential.left_chain_speed)
        self.set_right_side(self.differential.right_chain_speed)

    def odometry_test(self):
        self.go_forward()
        time.sleep(100)
        self.go_stop()
        print(self.odom.get_position())

    def set_mode(self, mode):
        self.mode = mode
        print("Mode changed to ", mode)

    def set_speed(self, speed):
        if speed > 100:
            speed = 100
        elif speed < 0:
            speed = 0
        self.speed = speed
        self.differential.max_speed = speed
        print("Speed changed to ", speed)

    def go_forward(self):
        self.set_right_side(self.speed)
        self.set_left_side(self.speed)
        if debug:
            print("Forward")

    def go_back(self):
        self.set_right_side(-self.speed)
        self.set_left_side(-self.speed)

    def go_right(self):
        self.set_right_side(self.speed)
        self.set_left_side(-self.speed)
        if debug:
            print("Right")

    def go_left(self):
        self.set_right_side(-self.speed)
        self.set_left_side(self.speed)
        if debug:
            print("Left")

    def go_stop(self):
        self.set_right_side(0.0)
        self.set_left_side(0.0)
        if debug:
            print("Stop")

    # Right side control
    def set_right_side(self, speed):
        self.left_speed = self.speed_normalize_function(speed)
        self.right_speed_odom = speed

    # Left side control
    def set_left_side(self, speed):
        self.right_speed = self.speed_normalize_function(speed)
        self.left_speed_odom = speed

    def speed_normalize_function(self, speed):
        in_min = -100
        in_max = 100
        out_min = 0
        out_max = 310
        return (speed - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def controller_data_sender(self):
        while self.running:
            if not debug:
                self.serial.send_data(f":ML={self.left_speed}!")
                self.serial.send_data(f":MR={self.right_speed}!")
                self.odom.update(self.left_speed_odom, self.right_speed_odom)

            #print(f":ML={self.left_speed}!")
            #print(f":MR={self.right_speed}!")
            time.sleep(0.02)  # Send data every 20ms


class SerialCommunication():
    def __init__(self, port, debug=False):
        if not debug:
            self.serial0 = serial.Serial(port)
            self.heart_beat = True

    def send_data(self, data):
        command_heart_beat = f":WD={int(self.heart_beat)}!"
        self.serial0.write(command_heart_beat.encode())
        self.serial0.write(data.encode())
        self.heart_beat = not self.heart_beat


serial = SerialCommunication(serial_port, debug)
controller = Controller(serial)

# Create Communication instance
communication = comunication.ReceiverController(server_address, server_port, controller)


# Start listening for incoming commands in a separate thread
listener_thread = threading.Thread(target=communication.listen, daemon=True)
listener_thread.start()

# Start sending controller data independently in a separate thread
sender_thread = threading.Thread(target=controller.controller_data_sender)
sender_thread.start()


# Handle Ctrl+C gracefully
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    del communication
    del serial
    del controller
    print("\nCtrl+C detected. Exiting gracefully...")
