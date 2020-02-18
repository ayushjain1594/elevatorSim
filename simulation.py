from __future__ import division
import simpy
import sys
from datetime import datetime as dt
from os import path

from elevator import Elevator
from elevatorcontrol import ElevatorControl
from trafficgenerator import TrafficGenerator
from printevent import print_event


RANDOM_SEED = 42
SIM_INIT_TIME = 0 # Initial simulation time
# SIM_TIME = 10  # units of time for which simulation should run
FLOORS = tuple(range(1, 10))
FLOOR_HEIGHT = 4  # in meters
MAX_ACCELERATION = 1  # in meters per second square, same deceleration
MAX_SPEED = 4  # in meters per second
EXP_DIST_LAMBDA = 10 # Generating interarrival time


class Simulation:
    def __init__(self, realtime=False):
        # create a simpy environment
        if realtime:
            self.env = simpy.rt.RealtimeEnvironment(
                initial_time=0, factor=0.05,
                strict=False)
        else:
            self.env = simpy.Environment()

        # create an elevator controller
        self.elevatorcontrol = ElevatorControl(
        	self.env, 1, FLOORS, 1, 
            FLOOR_HEIGHT, MAX_SPEED, MAX_ACCELERATION)

        # object to generate traffic
        self.traffic = TrafficGenerator(
        	self.env, EXP_DIST_LAMBDA, FLOORS)

    def run_service(self):
        while True:
            # wait until next arrival
            count, origin, destination, = \
                yield self.env.process(self.traffic.next_traffic())

            print_event(time=round(self.env.now, 1),
                event=f'Request arrived: {origin} to {destination}')
            
            self.elevatorcontrol.request_service(origin, destination, count)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        if path.exists('outputlog.txt'):
        	self.log = open('outputlog.txt', 'a')
        else:
        	self.log = open('outputlog.txt', '+w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # for python 3 capability
        pass

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		sys.stdout = Logger()
		print("\n\nSIMULATION started logging at" \
			+ f" {dt.strftime(dt.now(), '%m/%d/%Y %H:%M')}")
		print_event("TIME", "SYSTEM", "EVENT", "MESSAGE", "ETC")

		if len(sys.argv) == 3 and sys.argv[2].upper() == "REAL":
			sim = Simulation(realtime=True)
		else:
			sim = Simulation()

		sim.env.process(sim.run_service())

		try:
			sim.env.run(sys.argv[1])
		except ValueError as err:
			print("Error occured due to provided SIM_TIME")
			print("SIM_TIME must be > Simulation "\
			+ f"Initial time = {SIM_INIT_TIME}")
			print(err)
	else:
		print("Provide at least simulation time in format"+\
		": python simulation.py SIM_TIME")