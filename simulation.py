from __future__ import division
import simpy
from elevator import Elevator
from trafficgenerator import TrafficGenerator

SIM_TIME = 100  # units of time for which simulation should run
FLOORS = tuple(range(1, 10))
FLOOR_HEIGHT = 4  # in meters
MAX_ACCELERATION = 1  # in meters per second square, same deceleration
MAX_SPEED = 4  # in meters per second
EXP_DIST_LAMBDA = 10


class Simulation:
    def __init__(self):
        self.env = simpy.Environment()

        self.elevator = Elevator(self.env, FLOORS, FLOOR_HEIGHT, MAX_SPEED, MAX_ACCELERATION)
        self.traffic = TrafficGenerator(self.env, EXP_DIST_LAMBDA, FLOORS)

    def run_service(self):
        while True:
            pass
            # wait until next arrival
            count, origin, destination, = yield self.env.process(self.traffic.next_traffic())
            self.env.process(self.elevator.request_service(origin, destination))


if __name__ == '__main__':
    sim = Simulation()
    sim.env.process(sim.run_service())
    sim.env.run(SIM_TIME)
