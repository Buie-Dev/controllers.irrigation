from __future__ import annotations
from typing import TypedDict, Optional, List


class Subzone(TypedDict):
    id: int
    state: int


class PriorityQueueItem(TypedDict):
    id: str
    duration: float
    zone: int
    priority: int
    subzones: Optional[List[Subzone]]
    next: Optional[PriorityQueueItem]
    prev: Optional[PriorityQueueItem]
