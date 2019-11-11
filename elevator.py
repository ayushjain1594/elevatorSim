from __future__ import division
import simpy
import random
import numpy as np
from contextlib import suppress
import math


class Task:
    """
    Class: Creates a task object for elevators. Elevator object do not have visibility
    to request but their own tasks. ElevatorControl creates such tasks for elevators.
    """

    def __init__(self, elevator_object, task_type: ['hold', 'move', 'doors'],
        floor=None, floor_from=None, floor_to=None, count=None):

        self.elevator = elevator_object
        self.type = task_type

        if self.type == 'move':
            if (floor_from not in self.elevator.possible_states) or \
                (floor_to not in self.elevator.possible_states):
                raise ValueError('Destination floor is outside possible states')
            else:
                self.floor_from = floor_from
                self.floor_to = floor_to

        if self.type in ['doors', 'hold']:
            self.floor = floor

        if self.type == 'hold':
            if not isinstance(count, int):
                raise ValueError('People count must be integer')
            if count < 0:
                raise ValueError('People count cannot be negative number')
            self.count = count

    def timeout(self, time):
        """
        Method seprates simpy timeout from processes that may require to be
        interrupted. Simpy does not allow controlled interrupt of timeout processes.
        """
        if time >= 0:
            yield self.elevator.env.timeout(time)
            
    def go_to(self):
        """Method executes a 'move' type task and allows for interruption
        by ElevatorControl"""

        # get travel time
        travel_time = self.elevator.get_travel_time(self.floor_from, self.floor_to)

        # mark the start of execution
        task_start_time = self.elevator.env.now

        try:
            yield self.elevator.env.process(self.timeout(travel_time))

            # Once reached, update current state
            self.elevator.current_state = self.floor_to

        except simpy.Interrupt as interrupt:
            # If interruted, get cause
            cause = interrupt.cause
            if 'Go to:' in cause:
                try:
                    self.floor_to = int(cause[cause.index(':') + 1:])

                    # Initiate a new process
                    yield self.elevator.env.process(self.go_to(new_floor_to))

                except IndexError | ValueError:
                    pass

    def execute_task(self):

        if self.type == 'hold':
            #print(" "*25 + f'Holding elevator at floor {self.elevator.current_state} at time {round(self.elevator.env.now, 1)}')
            yield self.elevator.env.process(self.timeout(max(2, self.count)))

        if self.type == 'doors':
            yield self.elevator.env.process(self.timeout(0.5))

        if self.type == 'move':
            print(" "*25 + f'Moving elevator to {self.floor_to} at time {round(self.elevator.env.now, 1)}')
            yield self.elevator.env.process(self.go_to())


class Elevator:
    """Class: Creates an elevator object with properties such as current
    state (floor which elevator is at), speed, possible states (floors).
    Also, handles and acts on various requests"""

    def __init__(self, sim_env, floors: tuple, floor_height: float,
                 max_speed: float, max_accel: float):
        self.env = sim_env
        self.elevator = simpy.Resource(self.env)
        if type(floors) == tuple:
            self.possible_states = floors
        else:
            raise TypeError('Floors must be tuple!!')

        self.floor_height = floor_height

        self.current_state = random.choice(self.possible_states)
        self.speed = max_speed
        self.max_accel = max_accel
        self.kinematics = {'current_speed': 0,
                           'current_altitude': floor_height*(self.current_state - 1),
                           'current_acceleration': 0,
                           'max_speed': max_speed,
                           'max_acceleration': max_accel,
                           'time_to_max_speed': max_speed/max_accel}

        self.last_go_to_process = None

        self.tasks = {} # dictionary holding all tasks
        self.task_keys = []
        self.current_task_key = None
        

    def get_travel_time(self, floor_from: int, floor_to: int):
        """
        Method calculates travel time between two floors depending
        on elevator kinematics

        :param floor_from: (int)
        :param floor_to: (int)
        :return: (float) travel time
        """
        if (floor_from not in self.possible_states) or \
            (floor_to not in self.possible_states):
            return 0
        dist = abs(floor_from - floor_to)*self.floor_height

        if math.sqrt(dist*self.max_accel) < self.max_speed:
            time = round((2*dist)/math.sqrt(dist*self.max_accel), 1)

        else:    
            time = round((abs(floor_from - floor_to)*self.floor_height)/self.speed + \
            self.speed/self.max_accel, 1)

        return time

    def get_current_direction(self):
        """
        Method looks at the current state, current and future tasks 
        and returs one of - 'up', 'down', None

        :return (str or None) 'up'/'down'/None
        """
        if self.current_task_key is None:
            # if not executing any tasks
            return None

        else:
            # executing some task
            key_iterator = iter(self.current_task_key)
            current_task_type = next(key_iterator, None)

            if current_task_type in ['hold', 'doors']:
                index = 0

                # look at subsequent tasks to find 'move' type task
                while index < len(self.task_keys):
                    key_iterator = iter(self.task_keys[index])
                    next_task_type = next(key_iterator, None)
                    if next_task_type == 'move':
                        floor_from = next(key_iterator, None)
                        floor_to = next(key_iterator, None)

                        return 'up' if floor_to - floor_from > 0 \
                        else 'down'
                    index += 1

            elif current_task_type == 'move':
                floor_from = next(key_iterator, None)
                floor_to = next(key_iterator, None)

                return 'up' if floor_to - floor_from > 0 \
                else 'down'
        return None
    
    def process_tasks(self):
        """
        Method executes all the pending tasks for the elevator
        :return: None
        """

        # while there are pending tasks
        while len(self.tasks) > 1:
            # get key to next task
            self.current_task_key = self.task_keys.pop(0)

            # get the next task
            task = self.tasks[self.current_task_key]

            # execute and yield
            yield self.env.process(task.execute_task())

            # delete it from tasks
            del self.tasks[self.current_task_key]

        # after all the tasks are finished 
        self.current_task_key = None


if __name__ == '__main__':
    pass
