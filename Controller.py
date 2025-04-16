from time import sleep
import time
import copy
import json
from shared import pq, DESIRED_STATE
from RaspberryPi import RaspberryPi
from mqtt import publish_current_state, publish_queue

CURRENT_STATE = copy.deepcopy(DESIRED_STATE)
rp = RaspberryPi()


def turn_off_subzones(desired_item):
    subzones = desired_item.get("subzones")
    if subzones is not None:
        for subzone in subzones:
            subzone["state"] = 0


def turn_stop_time_off_other_queue_items(item, mqtt_client):
    current_item = pq.queue
    while current_item is not None:
        if current_item.start_time is not None and current_item.id != item.id:
            running_time = time.time() - current_item.start_time
            current_item.duration -= running_time
            current_item.start_time = None

            if current_item.duration <= 0:
                pq.remove_item(item.id)
                publish_queue(mqtt_client)
        current_item = current_item.next


def turn_off_other_relays(item):
    for desired_item in DESIRED_STATE:
        if desired_item["id"] == item.zone:
            continue

        desired_item["state"] = 0
        turn_off_subzones(desired_item)


def turn_off_relay(item):
    for desired_item in DESIRED_STATE:
        if desired_item["id"] != item.zone:
            continue
        desired_item["state"] = 0
        turn_off_subzones(desired_item)
        break


def item_control(item, mqtt_client):
    if item.start_time is None:
        # Item has not started yet
        zone = next((z for z in DESIRED_STATE if z["id"] == item.zone), None)

        # Set zone and subzones
        zone["state"] = 1

        if item.subzones is not None and zone.get("subzones") is not None:
            item_subzones_dict = {sz["id"]: sz["state"] for sz in item.subzones}
            for sz in zone["subzones"]:
                sz_id = sz.get("id")
                sz["state"] = item_subzones_dict.get(sz_id, 0)

        item.start_time = time.time()

        turn_stop_time_off_other_queue_items(item, mqtt_client)
        turn_off_other_relays(item)
        publish_queue(mqtt_client)

    running_time = time.time() - item.start_time
    item.duration -= running_time
    item.start_time = time.time()

    if item.duration <= 0:
        zone = next((z for z in DESIRED_STATE if z["id"] == item.zone), None)
        zone["state"] = 0
        turn_off_subzones(zone)
        pq.remove_item(item.id)
        publish_queue(mqtt_client)


def broadcast_changes(mqtt_client):
    global CURRENT_STATE
    current_state_string = json.dumps(CURRENT_STATE, sort_keys=True)
    desired_state_string = json.dumps(DESIRED_STATE, sort_keys=True)

    if current_state_string != desired_state_string:
        CURRENT_STATE = copy.deepcopy(DESIRED_STATE)
        publish_current_state(mqtt_client)
        rp.set_relays()


def controller(mqtt_client) -> None:

    while True:
        # pq.run()
        item = pq.queue
        if item == None:
            sleep(0.1)
            continue

        if item.remove:
            turn_off_relay(item)
            pq.remove_item(item.id)
            broadcast_changes(mqtt_client)
            publish_queue(mqtt_client)
            sleep(0.1)
            continue

        # Check for other removed items:
        next_item = item.next
        while next_item is not None:
            current_item = next_item
            next_item = next_item.next
            if current_item.remove:
                pq.remove_item(current_item.id)
                publish_queue(mqtt_client)

        item_control(item, mqtt_client)
        broadcast_changes(mqtt_client)

        sleep(1)
