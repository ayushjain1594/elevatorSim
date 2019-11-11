from __future__ import division
import simpy
from elevator import Elevator
from elevatorcontrol import ElevatorControl
from trafficgenerator import TrafficGenerator
import sys

RANDOM_SEED = 42
SIM_TIME = 10  # units of time for which simulation should run
FLOORS = tuple(range(1, 10))
FLOOR_HEIGHT = 4  # in meters
MAX_ACCELERATION = 1  # in meters per second square, same deceleration
MAX_SPEED = 4  # in meters per second
EXP_DIST_LAMBDA = 10


class Simulation:
    def __init__(self):
        # create a simpy environment
        self.env = simpy.Environment()

        self.elevatorcontrol = ElevatorControl(self.env, 1, FLOORS, 1, 
            FLOOR_HEIGHT, MAX_SPEED, MAX_ACCELERATION)
        self.traffic = TrafficGenerator(self.env, EXP_DIST_LAMBDA, FLOORS)

    def run_service(self):
        while True:
            # wait until next arrival
            count, origin, destination, = \
                yield self.env.process(self.traffic.next_traffic())

            print(f'Request arrived: {origin} to {destination}'+ \
                f' at {round(self.env.now, 1)}')
            
            self.elevatorcontrol.request_service(origin, destination, count)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Provide simulation time in format python simulation.py SIM_TIME")
    else:
        sim = Simulation()
        sim.env.process(sim.run_service())
        sim.env.run(sys.argv[1])
