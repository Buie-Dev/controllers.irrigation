import threading
import time

from Controller import controller
from mqtt import run_mqtt

if __name__ == "__main__":
    mqtt_client = run_mqtt()
    controller(mqtt_client)
