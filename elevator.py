from __future__ import division
import simpy
import random
import numpy as np
from contextlib import suppress


class Task:
    def __init__(self, elevator_object, task_type: ['hold', 'move', 'doors'],
        floor=None, count=None):
        self.elevator = elevator_object
        self.type = task_type

        if self.type == 'move':
            if floor is None:
                raise ValueError('Move type task requires destination floor')

            elif floor not in self.elevator.possible_states:
                raise ValueError('Destination floor is outside possible states')

            else:
                self.floor = floor

        if self.type == 'hold':
            if not isinstance(count, int):
                raise ValueError('Poeple count must be integer')

            if count < 0:
                raise ValueError('People count cannot be negative number')

            self.count = count

    def timeout(self, time):
        if time >= 0:
            yield self.elevator.env.timeout(time)
            
    def go_to(self, floor_override=None):
        current_floor = self.elevator.current_state # must be changed if recalled by interrupt
        if floor_override is None:
            travel_time = self.elevator.get_travel_time(current_floor, self.floor)
        else:
            travel_time = self.elevator.get_travel_time(current_floor, floor_override)

        task_start_time = self.elevator.env.now

        try:
            yield self.timeout(travel_time)
            self.elevator.current_state = self.floor \
                if floor_override is None else floor_override

        except Simpy.Interrupt as interrupt:
            cause = interrupt.cause
            if 'Go to:' in cause:
                try:
                    new_floor_to = int(cause[cause.index(':') + 1:])
                    self.go_to(new_floor_to)

                except IndexError | ValueError:
                    pass

    def execute_task(self):
        if self.type == 'hold':
            yield self.timeout(max(2, self.count))

        if self.type == 'doors':
            yield self.timeout(0.5)

        if self.type == 'move':
            yield self.go_to()


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
        time = round((abs(floor_from - floor_to)*self.floor_height)/self.speed + \
        self.max_speed/self.max_accel, 1)

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
                current_floor = next(key_iterator, None)
                index = 0

                # look at subsequent tasks to find 'move' type task
                # else update current floor
                while index < len(self.task_keys):
                    key_iterator = iter(self.task_keys[index])
                    next_task_type = next(key_iterator, None)

                    if next_task_type in ['hold', 'doors']:
                        current_floor = next(key_iterator, None)

                    elif next_task_type is 'move':
                        destination_floor = next(key_iterator, None)

                        return 'up' if destination_floor - current_floor > 0 \
                        else 'down'
                    index += 1

            elif current_task_type == 'move':
                # get the origin and destination
                current_floor = self.current_state
                destination_floor = next(key_iterator, None)

                return 'up' if destination_floor - current_floor > 0 \
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
            self.curent_task_key = self.task_keys.pop(0)

            # get the next task
            task = self.tasks[self.current_task_key]

            # execute and yield
            yield task.execute_task()

            # delete it from tasks
            del self.tasks[next_task_key]

        # after all the tasks are finished 
        self.current_task_key = None


if __name__ == '__main__':
    pass
