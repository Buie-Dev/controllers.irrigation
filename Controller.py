from time import sleep
import time
import copy
import json
from shared import pq, DESIRED_STATE
from RaspberryPi import RaspberryPi
from mqtt import publish_current_state

CURRENT_STATE = copy.deepcopy(DESIRED_STATE)


def item_control(item):
    if item.start_time is None:
        zone = next((z for z in DESIRED_STATE if z["id"] == item.zone), None)
        if zone:
            zone["state"] = 1
            if item.subzones is not None:
                zone["subzones"] = copy.deepcopy(item.subzones)

        item.start_time = time.time()
        # stop count on all others zones
        ri = item.next
        while ri is not None:
            ri.start_time = None
            if ri.start_time is not None:
                running_time = time.time() - ri.start_time
                ri.duration -= running_time
                if ri.duration <= 0:
                    pq.remove_item(item)
            ri = ri.next

    running_time = time.time() - item.start_time
    item.duration -= running_time
    item.start_time = time.time()

    if item.duration <= 0:
        zone = next((z for z in DESIRED_STATE if z["id"] == item.zone), None)
        if zone:
            zone["state"] = 0
            subzones = zone.get("subzones")
            if subzones is not None:
                for subzone in subzones:
                    subzone["state"] = 0
        pq.remove_item(item)


def controller(mqtt_client):
    global CURRENT_STATE
    rp = RaspberryPi()
    while True:
        # pq.run()
        item = pq.queue
        if item == None:
            sleep(0.1)
            continue

        item_control(item)

        current_state_string = json.dumps(CURRENT_STATE, sort_keys=True)
        desired_state_string = json.dumps(DESIRED_STATE, sort_keys=True)

        if current_state_string != desired_state_string:
            CURRENT_STATE = copy.deepcopy(DESIRED_STATE)
            publish_current_state(mqtt_client)
            rp.set_relays()

        sleep(1)
