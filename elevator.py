from __future__ import division
import simpy
import random
import numpy as np
from contextlib import suppress


class Elevator(object):
    """Class: Creates an elevator object with properties such as current
    state (floor which elevator is at), speed, possible states (floors).
    Also, handles and acts on various requests"""

    def __init__(self, sim_env, floors, speed):
        self.env = sim_env
        self.elevator = simpy.Resource(self.env)
        if type(floors) == tuple:
            self.possible_states = floors
        else:
            raise TypeError('Floors must be tuple!!')

        self.current_state = random.choice(self.possible_states)
        self.speed = speed
        self.kinematics = {'current_speed': 0,
                           'current_altitude': FLOOR_HEIGHT*(self.current_state - 1),
                           'current_acceleration': 0,
                           'max_speed': MAX_SPEED,
                           'max_acceleration': MAX_ACCELERATION,
                           'time_to_max_speed': MAX_SPEED/MAX_ACCELERATION}

        self.last_go_to_process = None

    def get_travel_time(self, floor_from: int, floor_to: int):
        """
        Method calculates travel time between two floors depending
        on elevator kinematics
        :param floor_from: (int)
        :param floor_to: (int)
        :return: (float) travel time
        """
        pass
    
    def bring_elevator(self, floor_at):
        if self.current_state != floor_at:
            yield self.env.timeout(abs(self.current_state - floor_at)/self.speed)
            print(f'Brought elevator from {self.current_state} to {floor_at}')
            self.current_state = floor_at

    def go_to_floor(self, floor_to):
        with suppress(simpy.Interrupt):
            self.last_go_to_process = self.env.timeout(abs(floor_to - self.current_state)/self.speed)
            yield self.last_go_to_process
            print(f'Reached floor {floor_to} at {self.env.now}')
            self.current_state = floor_to
            
    def request_service(self, floor_at: int, floor_to: int):
        """

        :param floor_at: (int) floor where the service is being requested at
        :param floor_to: (int) floor where the service is being requested to
        :return: None
        """
        print(f'Requesting elevator at floor {floor_at} to floor {floor_to} at time {self.env.now}')
        # change this to some central request processing system that takes
        # requests and queues them in a more realistic way
        with self.elevator.request() as req:
            yield req
            yield self.env.process(self.bring_elevator(floor_at))
            yield self.env.timeout(2)
            yield self.env.process(self.go_to_floor(floor_to))
        print('Finished service')


def wait_until_next_arrival():
    yield env.timeout(np.random.exponential())


def run_service():
    while True:
        # wait until next arrival
        yield env.timeout(np.random.exponential(10))

        req_at_floor = random.choice(FLOORS)
        req_to_floor = random.choice([floor for floor in FLOORS
                                      if floor != req_at_floor])
        env.process(elevator.request_service(req_at_floor, req_to_floor))


if __name__ == '__main__':
    env = simpy.Environment()
    FLOORS = tuple(range(1, 10))
    FLOOR_HEIGHT = 4  # in meters
    MAX_ACCELERATION = 1  # in meters per second square, same deceleration
    MAX_SPEED = 4  # in meters per second

    elevator = Elevator(env, FLOORS, 1)
    env.process(run_service())
    env.run(50)
