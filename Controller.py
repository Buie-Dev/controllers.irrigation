from time import sleep

from shared import pq


def controller():

    while True:

        pq.run()
        sleep(0.1)
