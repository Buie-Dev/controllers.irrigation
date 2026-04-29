from time import sleep
import time
import copy
import json
import threading
from date import today
import requests
from shared import pq, DESIRED_STATE, flow_tracker
from RaspberryPi import RaspberryPi
from mqtt import publish_current_state, publish_queue, publish_live_flow
from config import config

FLOW_PULSES_PER_LITRE = 330  # Digiten FL-608: F = 5.5 * Q (L/min) → 330 pulses/L
DEDICATED_LINE_TIMEOUT_S = 1800  # 30 min of no flow before submitting session to history
MIN_FLOW_DURATION_S = 5
NO_FLOW_MIN_DURATION_S = 30  # min run time (s) to record history when there is no flow

CURRENT_STATE = copy.deepcopy(DESIRED_STATE)
rp = RaspberryPi()


def submit_history(zone_id, start_dt, end_dt, pulses, subzones=None):
    duration = (end_dt - start_dt).total_seconds()
    if pulses == 0:
        if duration < NO_FLOW_MIN_DURATION_S:
            print(
                f"Ignoring no-flow run for zone {zone_id}: duration {duration:.1f}s < {NO_FLOW_MIN_DURATION_S}s"
            )
            return
    elif duration < MIN_FLOW_DURATION_S:
        print(
            f"Ignoring phantom flow for zone {zone_id}: duration < {MIN_FLOW_DURATION_S}s"
        )
        return
    active_subzone_ids = [sz["id"] for sz in (subzones or []) if sz.get("state") == 1]
    payload = {
        "zone_id": zone_id,
        "subzone_ids": active_subzone_ids,
        "litres": round(pulses / FLOW_PULSES_PER_LITRE, 2),
        "date": start_dt.strftime("%Y-%m-%d"),
        "start_time": start_dt.strftime("%H:%M:%S"),
        "end_time": end_dt.strftime("%H:%M:%S"),
    }

    def post():
        try:
            response = requests.post(
                f"{config.API_URL}/irrigations/history", json=payload, timeout=10
            )
            print(f"History submitted ({response.status_code}): {payload}")
        except Exception as e:
            print(f"Failed to submit history: {e}")

    threading.Thread(target=post, daemon=True).start()


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
        print(f"[item_control] starting zone={item.zone}, item.subzones={item.subzones}")
        zone = next((z for z in DESIRED_STATE if z["id"] == item.zone), None)

        # Set zone and subzones
        zone["state"] = 1

        if item.subzones is not None and zone.get("subzones") is not None:
            item_subzones_dict = {sz["id"]: sz["state"] for sz in item.subzones}
            for sz in zone["subzones"]:
                sz_id = sz.get("id")
                sz["state"] = item_subzones_dict.get(sz_id, 0)

        item.start_time = time.time()
        item.actual_start_datetime = today()

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
        end_dt = today()
        pulses = flow_tracker.reset_irrigation()
        if item.actual_start_datetime is not None:
            submit_history(item.zone, item.actual_start_datetime, end_dt, pulses, item.subzones)
        pq.remove_item(item.id)
        publish_queue(mqtt_client)


def check_dedicated_line_timeout():
    if (
        flow_tracker.last_dedicated_flow_time is not None
        and time.time() - flow_tracker.last_dedicated_flow_time
        > DEDICATED_LINE_TIMEOUT_S
    ):
        pulses, start_dt, end_dt = flow_tracker.flush_dedicated()
        if pulses > 0 and start_dt is not None:
            submit_history(None, start_dt, end_dt, pulses)


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
        check_dedicated_line_timeout()

        if item is None:
            sleep(0.1)
            continue

        if item.remove:
            turn_off_relay(item)
            if item.actual_start_datetime is not None:
                end_dt = today()
                pulses = flow_tracker.reset_irrigation()
                submit_history(item.zone, item.actual_start_datetime, end_dt, pulses, item.subzones)
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
        # Publish live flow if the item is still the active run
        if (
            pq.queue is not None
            and pq.queue.id == item.id
            and item.actual_start_datetime is not None
        ):
            litres = flow_tracker.irrigation_pulses / FLOW_PULSES_PER_LITRE
            publish_live_flow(mqtt_client, item.id, litres)
        broadcast_changes(mqtt_client)

        sleep(1)
