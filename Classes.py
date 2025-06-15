from typing import List, Optional, Union


class QueueItem:

    def __init__(
        self,
        id: str,
        duration: float,
        zone: int,
        priority: int,
        subzones=Optional[List[Union[int, str]]],
    ):
        self.id = id
        self.duration = int(duration * 60)
        self.zone = zone
        self.priority = priority
        self.subzones = subzones
        self.next = None
        self.prev = None
        self.start_time = None
        self.end_time = None
        self.remove = False

    def to_object(self):
        return {
            "id": self.id,
            "duration": self.duration,
            "zone": self.zone,
            "priority": self.priority,
            "subzones": self.subzones,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def print_item(self):
        print(
            "Id: {}, Zone: {}, Priority: {}, Duration: {}, Next: {}, Prev: {}, Remove: {}".format(
                self.id,
                self.zone,
                self.priority,
                self.duration,
                self.next.id if self.next else "None",
                self.prev.id if self.prev else "None",
                self.remove,
            )
        )
        print("")
