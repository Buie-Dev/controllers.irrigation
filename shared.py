import time
from datetime import datetime
from PriorityQueue import PriorityQueue


class FlowTracker:
    def __init__(self):
        self.irrigation_pulses = 0
        self.dedicated_pulses = 0
        self.dedicated_start_dt = None
        self.dedicated_first_flow_time = None
        self.last_dedicated_flow_time = None

    def add_irrigation_pulses(self, count):
        self.irrigation_pulses += count

    def reset_irrigation(self):
        pulses = self.irrigation_pulses
        self.irrigation_pulses = 0
        return pulses

    def add_dedicated_pulses(self, count):
        if self.dedicated_start_dt is None:
            self.dedicated_start_dt = datetime.now()
            self.dedicated_first_flow_time = time.time()
        self.dedicated_pulses += count
        self.last_dedicated_flow_time = time.time()

    def flush_dedicated(self):
        """Returns (pulses, start_dt, end_dt, duration_s) and resets state."""
        duration_s = self.last_dedicated_flow_time - self.dedicated_first_flow_time
        data = (self.dedicated_pulses, self.dedicated_start_dt, datetime.now(), duration_s)
        self.dedicated_pulses = 0
        self.dedicated_start_dt = None
        self.dedicated_first_flow_time = None
        self.last_dedicated_flow_time = None
        return data


# Shared variables
pq = PriorityQueue()
flow_tracker = FlowTracker()
DESIRED_STATE = [
    # Upper Level
    {"id": 1, "state": 0},
    {"id": 2, "state": 0},
    {"id": 3, "state": 0},
    {"id": 4, "state": 0},
    {"id": 5, "state": 0},
    {"id": 6, "state": 0},
    {"id": 7, "state": 0},
    {"id": 8, "state": 0},
    {"id": 9, "state": 0},
    {"id": 10, "state": 0},
    {"id": 11, "state": 0},
    {"id": 12, "state": 0},
    # Lower level
    {"id": 13, "state": 0},
    {"id": 14, "state": 0},
    {"id": 15, "state": 0},
    {"id": 16, "state": 0},
    {"id": 17, "state": 0},
    {"id": 18, "state": 0},
    {"id": 19, "state": 0},
    {
        "id": 20,
        "state": 0,
        "subzones": [
            {"id": 1, "state": 0},
            {"id": 2, "state": 0},
            {"id": 3, "state": 0},
            {"id": 4, "state": 0},
            {"id": 5, "state": 0},
            {"id": 6, "state": 0},
            {"id": 7, "state": 0},
            {"id": 8, "state": 0},
            {"id": 9, "state": 0},
            {"id": 10, "state": 0},
            {"id": 11, "state": 0},
            {"id": 12, "state": 0},
        ],
    },
]
