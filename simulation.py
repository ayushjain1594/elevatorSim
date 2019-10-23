from __future__ import division
import simpy


class Simulation(object):
    def __init__(self):
        self.env = simpy.Environment()

    def setup_simulation(self):
        pass
        # create elevator object

        # traffic generator object

    def run_elevator(self):
        while True:
            pass
            # wait until the next traffic arrival

            # get new traffic configuration - # people, floor, etc

            # start request process


if __name__ == '__main__':
    pass
