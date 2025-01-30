import json
import uuid

import paho.mqtt.client as mqtt

from config import config
from PriorityQueue import QueueItem
from shared import lock, pq

TOPIC_SUB_IRRIGATION_REQUEST = "irrigation/request"
TOPIC_SUB_HEALTH_CHECK_REQUEST = "healthcheck/request"  # Topic to subscribe to
TOPIC_SUB_HEALTH_CHECK_RESPONSE = "healthcheck/response"

TOPIC_PUB_HEALTH_CHECK_RESPONSE = "healthcheck/response"  # Topic to publish to

sub_topics = [
    TOPIC_SUB_HEALTH_CHECK_RESPONSE,
    TOPIC_SUB_HEALTH_CHECK_REQUEST,
    TOPIC_SUB_IRRIGATION_REQUEST,
]


# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker!")
        for topic in sub_topics:
            client.subscribe(topic)  # Subscribe to a topic after connecting
    else:
        print(f"Connection failed with code {rc}")


def health_check_response(client):
    payload = {"device": config.DEVICE_NAME}
    client.publish(TOPIC_PUB_HEALTH_CHECK_RESPONSE, json.dumps(payload))


# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    try:

        if msg.topic == TOPIC_SUB_IRRIGATION_REQUEST:
            payload = json.loads(msg.payload.decode())
            item_id = uuid.uuid4()
            duration = payload["duration"]
            zone = payload["zone"]
            priority = payload["priority"]
            sub_zones = payload.get("sub_zones")

            item = QueueItem(item_id, duration, zone, priority, sub_zones)

            with lock:
                pq.insert_new_item(item)
        elif msg.topic == TOPIC_SUB_HEALTH_CHECK_REQUEST:
            health_check_response(client)

    except json.JSONDecodeError:
        print(f"Received non-JSON message: {msg.payload.decode()} on topic {msg.topic}")


def create_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    return client


def run_mqtt():
    try:
        client = create_mqtt_client()

        print(f"Connecting to broker {config.MQTT_BROKER} on port {config.MQTT_PORT}")
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_start()

        # Keep the script running to listen for incoming messages
        # input("Press Enter to exit...\n")
        while True:
            pass

    finally:
        # Disconnect gracefully
        client.loop_stop()
        client.disconnect()
        print("Disconnected from broker")
