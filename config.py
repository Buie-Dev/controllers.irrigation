import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_PORT = int(os.getenv("MQTT_PORT"))
    DEVICE_NAME = os.getenv("DEVICE_NAME")

    IS_RASPBERRYPI = os.getenv("ENVIRONEMNT") == "raspberry_pi"


# Export the configuration object for importing
config = Config()
