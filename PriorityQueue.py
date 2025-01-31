import time
from typing import List, Optional, Union

from RaspberryPi import RaspberryPi


class QueueItem:

    def __init__(
        self,
        id: str,
        duration: float,
        zone: int,
        priority: int,
        sub_zones=Optional[List[Union[int, str]]],
    ):
        self.id = id
        self.duration = duration
        self.zone = zone
        self.priority = priority
        self.sub_zones = sub_zones
        self.next = None
        self.prev = None
        self.start_time = None
        self.end_time = None

    def print_item(self):
        print(
            "Id: {}, Zone: {}, Priority: {}, Duration: {}, Next: {}, Prev: {}".format(
                self.id,
                self.zone,
                self.priority,
                self.duration,
                self.next.id if self.next else "None",
                self.prev.id if self.prev else "None",
            )
        )


class PriorityQueue:
    queue = None
    raspberry_pi = RaspberryPi()

    def run(self):
        item = self.queue
        if item == None:
            return

        if item.start_time is None:
            self.raspberry_pi.turn_on_relay(item.zone)
            item.start_time = time.time()
            # stop count on all others zones
            ri = item.next
            while ri is not None:
                ri.start_time = None
                if ri.start_time is not None:
                    running_time = time.time() - ri.start_time
                    ri.duration -= running_time
                    if ri.duration <= 0:
                        self.remove_item(item)
                ri = ri.next

        running_time = time.time() - item.start_time
        item.duration -= running_time
        item.start_time = time.time()

        if item.duration <= 0:
            self.raspberry_pi.turn_off_relay(item.zone)
            self.remove_item(item)

    def insert_new_item(self, item: QueueItem):
        current_item = self.queue
        if current_item is None:
            self.queue = item
            return

        while current_item is not None:

            if current_item.priority > item.priority:
                if current_item.prev is not None:
                    current_item.prev.next = item
                else:
                    self.queue = item
                item.next = current_item
                item.prev = current_item.prev
                current_item.prev = item
                return

            elif current_item.next == None:
                current_item.next = item
                item.prev = current_item
                return
            else:
                current_item = current_item.next

    def display(self):

        ci = self.queue
        if self.queue is not None:
            print("")
        while ci is not None:
            ci.print_item()
            ci = ci.next

    def remove_item(self, item: QueueItem):

        current_item = self.queue
        while current_item is not None:
            if current_item.id == item.id:
                if current_item.next is not None:
                    current_item.next.prev = current_item.prev

                if current_item.prev is not None:
                    current_item.prev.next = current_item.next
                else:
                    self.queue = current_item.next

                if current_item.next == current_item.prev:
                    self.queue = None

                current_item.next = None

                current_item.prev = None
                return

            current_item = current_item.next
