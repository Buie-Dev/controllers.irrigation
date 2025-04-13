import time
from typing import Optional
import json
from ObjectTypes import PriorityQueueItem
from Classes import QueueItem


class PriorityQueue:
    queue: Optional[PriorityQueueItem] = None

    def insert_new_item(self, item: QueueItem) -> None:
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

    def display(self) -> None:

        current_item = self.queue
        if self.queue is not None:
            print("")
        while current_item is not None:
            current_item.print_item()
            current_item = current_item.next

    def remove_item(self, item_id: str) -> None:

        current_item = self.queue
        while current_item is not None:
            if current_item.id == item_id:
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

    def set_remove_item_state(self, item_id: str) -> None:
        current_item = self.queue
        while current_item is not None:
            if current_item.id == item_id:
                current_item.remove = True
                break

    def set_remove_all_state(self) -> None:
        current_item = self.queue
        while current_item is not None:
            current_item.remove = True
            current_item = current_item.next

    def remove_all(self):
        current_item = self.queue
        while current_item is not None:
            next_item = current_item.next
            self.remove_item(current_item.id)
            current_item = next_item

    def to_json(self) -> list:
        results = []
        current_item = self.queue
        while current_item is not None:
            results.append(current_item.to_object())
            current_item = current_item.next
        return results

    def print(self) -> None:
        current_item = self.queue
        if current_item is None:
            print(" Priority Queue is Empty")
        while current_item is not None:
            current_item.print_item()
            current_item = current_item.next
