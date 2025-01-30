from time import sleep

from shared import lock, pq


def controller():

    while True:

        with lock:
            pq.display()
            pq.run()
            sleep(0.1)
