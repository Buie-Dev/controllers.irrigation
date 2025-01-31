import threading
import time

from Controller import controller
from mqtt import run_mqtt

if __name__ == "__main__":
    run_mqtt()
    controller()

    # producer_thread = threading.Thread(target=run_mqtt)
    # consumer_thread = threading.Thread(target=controller)

    # producer_thread.start()
    # consumer_thread.start()

    # producer_thread.join()
    # consumer_thread.join()
