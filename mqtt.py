import json
import uuid
import paho.mqtt.client as mqtt

from config import config
from PriorityQueue import QueueItem
from shared import pq, DESIRED_STATE

TOPIC_SUB_IRRIGATION_REQUEST = "irrigation/request"
TOPIC_SUB_IRRIGATION_STOP = "irrigation/stop"
TOPIC_SUB_IRRIGATION_STOP_ALL = "irrigation/stopAll"
TOPIC_SUB_HEALTH_CHECK_REQUEST = "healthcheck/request"

TOPIC_PUB_HEALTH_CHECK_RESPONSE = "healthcheck/response"  # Topic to publish to
TOBIC_PUB_CURRENT_STATE = "irrigation/currentState"
TOBIC_PUB_IRRIGATION_QUEUE = "irrigation/queue"

sub_topics = [
    TOPIC_SUB_HEALTH_CHECK_REQUEST,
    TOPIC_SUB_IRRIGATION_REQUEST,
    TOPIC_SUB_IRRIGATION_STOP,
    TOPIC_SUB_IRRIGATION_STOP_ALL,
]

print(
    "CONFIG.MQTT",
    config.MQTT_BROKER,
    config.MQTT_PASSWORD,
    config.MQTT_PORT,
    config.MQTT_USERNAME,
)


# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker!")
        publish_current_state(client)
        publish_queue(client)
        for topic in sub_topics:
            client.subscribe(topic)  # Subscribe to a topic after connecting
    else:
        print(f"Connection failed with code {rc}")


def health_check_response(client):
    payload = {"device": config.DEVICE_NAME}
    publish_message(client, TOPIC_PUB_HEALTH_CHECK_RESPONSE, payload)


def publish_message(client, topic, payload, retain=False):
    try:
        message = json.dumps(payload)
        client.publish(topic, message, retain=retain)
        print(f"Published to {topic}: Retain: {retain}: {message}")
    except Exception as e:
        print(f"Error publishing message: {e}")


def publish_current_state(client):
    publish_message(client, TOBIC_PUB_CURRENT_STATE, DESIRED_STATE)


def publish_queue(client):
    publish_message(client, TOBIC_PUB_IRRIGATION_QUEUE, pq.to_json())


# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    # print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    try:
        if msg.topic == TOPIC_SUB_IRRIGATION_REQUEST:
            payload = json.loads(msg.payload.decode())
            item_id = str(uuid.uuid4())
            duration = payload["duration"]
            zone = payload["zone"]
            priority = payload["priority"]
            subzones = payload.get("subzones")
            item = QueueItem(item_id, duration, zone, priority, subzones)
            pq.insert_new_item(item)
            publish_queue(client)

        elif msg.topic == TOPIC_SUB_IRRIGATION_STOP:
            payload = json.loads(msg.payload.decode())
            item_id = payload["id"]
            pq.remove_item(item_id)
            publish_queue(client)
        elif msg.topic == TOPIC_SUB_IRRIGATION_STOP_ALL:
            pq.remove_all()
            publish_queue(client)
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
        return client

    finally:
        pass
