import numpy as np
import random


class TrafficGenerator:
    """Object of this class generates traffic requesting
    service from elevator(s)."""
    def __init__(self, environment, dist_lambda: float, floors: tuple):
        """
        Initialize the traffic object
        """
        self.env = environment
        if dist_lambda > 0:
            self.dist_lambda = dist_lambda
        else:
            raise ValueError("Lambda for exponential distribution must be positive")

        if type(floors) == tuple:
            self.floors = floors
        else:
            raise TypeError("Floors must be of type tuple")

    def generate_time(self):
        return np.random.exponential(self.dist_lambda)

    @staticmethod
    def generate_count():
        return random.randint(1, 6)

    def generate_origin_destination(self):
        origin = random.choice(self.floors)
        destination = random.choice([floor for floor in self.floors
                                     if floor != origin])
        return origin, destination

    def time_out(self, time):
        """
        Method calls simpy timeout with required time
        :param time: int or float
        :return: None
        """
        if time > 0:
            yield self.env.timeout(time)

    def next_traffic(self):
        """
        Method returns random configuration of traffic
        at every call
        :return: count of people, origin floor, destination floor
        """
        yield self.env.process(self.time_out(self.generate_time()))
        count = random.randint(1, 6)
        origin, destination = self.generate_origin_destination()

        return count, origin, destination
