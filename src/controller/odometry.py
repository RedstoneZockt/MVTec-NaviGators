import math
import time


class ChainDriveOdometry:
    def __init__(self):
        """
        Initialize the odometry system.
        :param wheelbase: Distance between the left and right chain (meters).
        :param dt: Time step for updates (seconds).
        """
        self.x = 0.0  # X position (meters)
        self.y = 0.0  # Y position (meters)
        self.theta = 0.0  # Orientation (radians)
        self.factor = 0.006

        self.wheelbase = 0.19  # Distance between chains
        self.current_time = time.time()

    def update(self, v_left, v_right):
        """
        Update the robot's estimated position based on commanded velocities.
        :param v_left: Commanded velocity of left chain (m/s).
        :param v_right: Commanded velocity of right chain (m/s).
        """
        v_left = v_left * self.factor
        v_right = v_right * self.factor
        self.actual_time = time.time()
        self.dt = self.actual_time - self.current_time
        self.current_time = self.actual_time
        # Compute linear and angular velocity
        v = (v_left + v_right) / 2.0  # Linear velocity
        omega = (v_right - v_left) / self.wheelbase  # Angular velocity

        # Update position using simple kinematics
        delta_x = v * math.cos(self.theta) * self.dt
        delta_y = v * math.sin(self.theta) * self.dt
        delta_theta = omega * self.dt

        self.x += delta_x
        self.y += delta_y
        self.theta += delta_theta

        # Keep theta within -π to π
        while self.theta > math.pi:
            self.theta -= 2 * math.pi
        while self.theta < -math.pi:
            self.theta += 2 * math.pi

    def get_position(self):
        """
        Get the current estimated position and orientation.
        :return: (x, y, theta) tuple.
        """
        return self.x, self.y, self.theta

# Example Usage
# if __name__ == "__main__":
#     wheelbase = 0.5  # Distance between left and right chain (meters)
#     dt = 0.1  # Time step (seconds)

#     odometry = ChainDriveOdometry(wheelbase, dt)

#     # Simulate movement
#     commands = [
#         (1.0, 1.0),  # Move straight
#         (1.0, 0.5),  # Turn right
#         (0.5, 1.0),  # Turn left
#         (1.0, 1.0)   # Move straight
#     ]

#     for v_left, v_right in commands:
#         odometry.update(v_left, v_right)
#         print("Position:", odometry.get_position())
