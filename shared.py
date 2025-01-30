import threading

from PriorityQueue import PriorityQueue

# Shared variable
pq = PriorityQueue()

# Lock for thread synchronization
lock = threading.Lock()
