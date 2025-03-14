import comunication
import time
import threading

ip_address = '127.0.0.1'
controller_port = 4000
search_algorithm_port = 5000

communication_controller = comunication.Transceiver(ip_address, controller_port)
communication_search = comunication.Receiver(ip_address, search_algorithm_port)

class Manager:
    def __init__(self
                 , search):
        self.search = search
        self.running = True

    def __del__(self):
        self.running = False

    def state_update(self):
        while self.running:
            if communication_search.data == "s":
                self.search.searching = True
            elif communication_search.data == "f":
                self.search.i = 0
                self.search.searching = False
                communication_controller.send_data("S")




class SearchAlgorithm:
    def __init__(self):
        communication_controller.send_data('M1')
        communication_controller.send_data('S60')
        self.searching = False
        self.running = True
        self.turning_time = 0.5
        self.forward_time = 1
        self.forward_speed = 50
        self.turning_speed = 100
        self.i = 0
        # [command, duration, speed]
        self.searching_command_list = [['F', self.forward_time, self.forward_speed],
                                       ['L', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['R', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['R', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['L', self.turning_time, self.turning_speed]]

    def __del__(self):
        self.running = False

    def search(self):

        while self.running:
            if self.searching:
                communication_controller.send_data('S' + str(self.searching_command_list[self.i][2]))
                self.interval_sender(self.searching_command_list[self.i][1], 0.05, self.searching_command_list[self.i][0])
                self.i+=1
                if self.i == len(self.searching_command_list):
                    self.i = 0



    def interval_sender(self, duration, interval, command):
        # Assuming communication_controller is already initialized
        start_time = time.time()  # Get the current time
        while (time.time() - start_time) < duration and self.searching:
            communication_controller.send_data(command)
            time.sleep(interval)  # Wait for 200 ms before sending again


search_algorithm = SearchAlgorithm()
manager = Manager(search_algorithm)


# Start listening for incoming commands in a separate thread
search_thread = threading.Thread(target=search_algorithm.search, daemon=True)
search_thread.start()

# Start listening for incoming commands in a separate thread
manager_thread = threading.Thread(target=manager.state_update, daemon=True)
manager_thread.start()

communication_search_thread = threading.Thread(target=communication_search.listen, daemon=True)
communication_search_thread.start()
# Handle Ctrl+C gracefully
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    del communication_search
    del search_algorithm
    del manager
    print("\nCtrl+C detected. Exiting gracefully...")




