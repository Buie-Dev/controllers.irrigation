import time
from typing import Optional
from shared import DESIRED_STATE
from config import config

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    print(config.IS_RASPBERRYPI)
    print("Running on non-Raspberry Pi hardware. Using mock GPIO library.")


class RaspberryPi:
    # pin_numbers = [14, 15, 18, 23, 24, 25, 8, 7, 2, 3, 4, 17, 27, 22, 10, 9]
    pin_numbers = [
        2,
        3,
        4,
        17,
        27,
        22,
        10,
        9,
        11,
        0,
        5,
        6,
        14,
        15,
        18,
        23,
        240,
        25,
        8,
        7,
    ]

    def __init__(self):
        if config.IS_RASPBERRYPI:
            GPIO.setmode(GPIO.BCM)  # Use BCM numbering
            for pin in self.pin_numbers:
                GPIO.setup(pin, GPIO.OUT)  # Set all as output
                GPIO.output(pin, GPIO.HIGH)

    def turn_all_off(self):
        self.active_zone = None
        print("TURNING OFF ALL RELAY")
        for pin in self.pin_numbers:
            if config.IS_RASPBERRYPI:
                GPIO.output(pin, GPIO.HIGH)
            else:
                print(f"TURNING OFF PIN {pin}")

    def turn_on_relay(self, zone: int):

        self.turn_all_off()
        pin_number = self.pin_numbers[zone - 1]

        if config.IS_RASPBERRYPI:
            GPIO.output(pin_number, GPIO.LOW)
        else:
            print(f"TURNING ON ZONE {zone}: GPIO {pin_number}")

    def turn_off_relay(self, zone: int):

        pin_number = self.pin_numbers[zone - 1]

        if config.IS_RASPBERRYPI:
            print("TURNING OFF RELAY")
            GPIO.output(pin_number, GPIO.HIGH)
        else:
            print(f"TURNING OFF ZONE {zone}: GPIO {pin_number}")

    def set_relays(self):
        for index, zone in enumerate(DESIRED_STATE):
            pin_number = self.pin_numbers[index]

            if config.IS_RASPBERRYPI:
                state = GPIO.HIGH if zone["state"] == 0 else GPIO.LOW
                GPIO.output(pin_number, state)
            else:
                print(
                    f"SETTING ZONE {zone['id']}: GPIO {pin_number} TO {zone['state']}"
                )
