import comunication
import time
import threading

ip_address = '127.0.0.1'
controller_port = 3000
search_algorithm_port = 5000

communication_controller = comunication.Transceiver(ip_address, controller_port)
communication_search = comunication.Receiver(ip_address, search_algorithm_port)

class Manager:
    def __init__(self, search):
        self.search = search
        self.running = True

    def __del__(self):
        self.running = False

    def state_update(self):
        while self.running:
            if communication_search.data == "Search":
                self.search.searching = True
            elif communication_search.data == "Found":
                self.search.searching = False




class SearchAlgorithm:
    def __init__(self):
        communication_controller.send_data('M1')
        communication_controller.send_data('S80')
        self.searching = False
        self.running = True
        self.turning_time = 1
        self.forward_time = 3

        # [command, duration]
        self.searching_command_list = [['F', self.forward_time], ['L', self.turning_time], ['F', self.forward_time], ['R', self.turning_time], ['F', self.forward_time], ['R', self.turning_time], ['F', self.forward_time], ['L', self.turning_time]]

    def __del__(self):
        self.running = False

    def search(self):
        i = 0
        while self.running:
            if self.searching:
                self.interval_sender(self.searching_command_list[i][1], 0.2, self.searching_command_list[i][0])
                i+=1
                if i == len(self.searching_command_list):
                    i = 0


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




