import serial

ser = serial.Serial('/dev/ttyUSB0')  # open serial port
print(ser.name)

chain_velocity: int = 170

command_left: str = ":ML=" + str(chain_velocity) + "!"
command_right: str = ":MR=" + str(chain_velocity) + "!"

ser.write(command_left)
ser.write(command_right)

