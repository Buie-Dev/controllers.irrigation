# CLAUDE.md

## What this repo is

Python service for a Raspberry Pi that manages an irrigation priority queue and controls zone relays via MQTT. It receives irrigation requests, queues them by priority, runs a 1-second tick loop that controls GPIO relay state, tracks water flow from sensors, and submits completed run history to the API. It also publishes live flow data and current zone states over MQTT for the mobile and web apps to display.

## Related repos

- [home-server.infra](https://github.com/Buie-Dev/home-server.infra) — Docker Compose infrastructure, runs the Mosquitto MQTT broker
- [controllers.garden](https://github.com/Buie-Dev/controllers.garden) — Raspberry Pi Zero 2W that subscribes to `irrigation/currentState` and sets GPIO relays
- [devices.flow-sensor](https://github.com/Buie-Dev/devices.flow-sensor) — ESP32 flow sensor that publishes pulse counts to `irrigation/flow`
- [automations.irrigation](https://github.com/Buie-Dev/automations.irrigation) — Schedule automation service that publishes to `irrigation/request`
- [home-server.api](https://github.com/Buie-Dev/home-server.api) — Flask REST API, receives `POST /irrigations/history`
- [home-server.web](https://github.com/Buie-Dev/home-server.web) — React web app
- [home-server.mobile](https://github.com/Buie-Dev/home-server.mobile) — React Native mobile app

## Stack

- Python 3.9 on Raspberry Pi
- paho-mqtt for MQTT pub/sub
- RPi.GPIO for relay control (active LOW)
- requests for REST API calls (history submission)
- Docker Compose (privileged mode, host network)

## Commands

```bash
docker compose up -d       # Start the service
docker compose logs -f     # Tail logs
docker compose down        # Stop the service
```

## File layout

```
index.py              # Entry point — starts MQTT client, then runs controller loop
Controller.py         # Main loop — tick-based queue processing, flow tracking, history submission
mqtt.py               # MQTT client — subscribes to request/stop/flow topics, publishes state/queue/liveFlow
PriorityQueue.py      # Doubly-linked-list priority queue sorted by priority
Classes.py            # QueueItem data class (id, duration, zone, priority, subzones)
ObjectTypes.py        # TypedDict definitions for type annotations
RaspberryPi.py        # GPIO relay control — 20 pins, active LOW, set_relays from DESIRED_STATE
shared.py             # Shared state — PriorityQueue instance, DESIRED_STATE (20 zones), FlowTracker
date.py               # Timezone-aware datetime helper (America/Vancouver)
config.py             # Config class reading from environment variables
docker-compose.yaml   # Single service, privileged, host network, .env file
Dockerfile            # Python 3.9 base, installs requirements
requirements.txt      # paho-mqtt, python-dotenv, uuid, certifi, requests
requirements_pi.txt   # RPi.GPIO
.env                  # Credentials and config (gitignored)
.env.example          # Template for .env
```

## MQTT topics

| Direction | Topic | Payload |
|---|---|---|
| Subscribe | `irrigation/request` | `{ duration, zone, priority, subzones? }` — queue a new run |
| Subscribe | `irrigation/stop` | `{ id }` — flag a single queue item for removal |
| Subscribe | `irrigation/stopAll` | Any — flag all queue items for removal |
| Subscribe | `irrigation/flow` | `{ sensor, pulse_count }` — flow sensor pulse data |
| Subscribe | `healthcheck/request` | Any — triggers health response |
| Publish | `irrigation/currentState` | Zone state array (retained) |
| Publish | `irrigation/queue` | Serialized priority queue (retained) |
| Publish | `irrigation/liveFlow` | `{ id, litres }` per second during active run |
| Publish | `healthcheck/response` | `{ device: DEVICE_NAME }` |

## How the queue works

The priority queue is a doubly-linked list sorted by priority number. The head item is the active run. When a new request arrives, it is inserted in priority order. The controller loop ticks every second, decrementing the active item's duration. When duration hits zero, the run is complete and history is submitted. Stop requests set a `remove` flag that the controller checks on the next tick, allowing thread-safe removal.

## Flow tracking

Two flow sensors publish to `irrigation/flow` with different sensor names. The irrigation flow sensor's pulses are tracked during active runs (330 pulses per litre, Digiten FL-608). The dedicated line sensor tracks independent usage and auto-submits history after 30 minutes of no flow.

## Standards

- Two long-lived branches: `main` (stable) and `dev` (ongoing work)
- Spec branches named `spec/NNN-short-name`, branched from `dev`, merged back to `dev`
- Commit messages: imperative, sentence case, no AI attribution
- `.gitignore` covers `.env`, `__pycache__/`
- `.env.example` lists every variable with placeholder values
- No license file

## Boundaries

- Never push. Give commands and wait for confirmation.
- Never change app behavior unless a spec says to.
- Never commit `.env`, real IPs, or credentials.
- Never merge a pull request. I review and merge.
- Only write things that are true in the code.

## Workflow

Changes start as specs in `docs/specs/`. Claude Code implements them on a spec branch, and I review and merge every pull request.
