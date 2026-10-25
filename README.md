![CI](https://github.com/Buie-Dev/controllers.irrigation/actions/workflows/ci.yml/badge.svg?branch=dev)

# controllers.irrigation

Raspberry Pi service that manages an irrigation priority queue and controls zone relays via MQTT.

## Why I built it

I needed something to sit between the apps and the physical relays that could handle multiple irrigation requests at once. This service receives requests over MQTT, queues them by priority, runs each one for the requested duration, tracks water flow from sensors, and logs completed runs to the API. The mobile app and web app show the live queue state and flow data while irrigation is running.

## How it fits

This runs on a dedicated Raspberry Pi wired to a 20-zone relay board. It is the central coordinator between the apps, the automation service, the garden controller, and the flow sensors.

- [home-server.infra](https://github.com/Buie-Dev/home-server.infra) runs the Mosquitto MQTT broker and shared infrastructure
- [controllers.garden](https://github.com/Buie-Dev/controllers.garden) subscribes to `irrigation/currentState` and sets GPIO relays on a separate Pi
- [devices.flow-sensor](https://github.com/Buie-Dev/devices.flow-sensor) publishes flow sensor pulse data to `irrigation/flow`
- [automations.irrigation](https://github.com/Buie-Dev/automations.irrigation) triggers scheduled runs by publishing to `irrigation/request`
- [home-server.api](https://github.com/Buie-Dev/home-server.api) is the Flask REST API that receives completed run history
- [home-server.web](https://github.com/Buie-Dev/home-server.web) and [home-server.mobile](https://github.com/Buie-Dev/home-server.mobile) display zone states, queue, and live flow

## Stack

- Python 3.9 on Raspberry Pi
- paho-mqtt for MQTT pub/sub
- RPi.GPIO for relay control (active LOW)
- requests for REST API calls (history submission)
- Docker Compose (privileged mode, host network)

## Running it locally

### Prerequisites

- Raspberry Pi with Docker installed
- 20-zone relay board wired to GPIO (see pin mapping below)
- Network access to the MQTT broker and API

### First time setup

1. Clone the repo

```bash
git clone https://github.com/Buie-Dev/controllers.irrigation.git
cd controllers.irrigation
```

2. Create `.env` from the example and fill in your credentials

```bash
cp .env.example .env
```

3. Start the service

```bash
docker compose up -d
```

## Configuration

| Variable | Purpose |
|---|---|
| `MQTT_USERNAME` | MQTT broker username |
| `MQTT_PASSWORD` | MQTT broker password |
| `MQTT_BROKER` | MQTT broker IP address |
| `MQTT_PORT` | MQTT broker port (1883) |
| `DEVICE_NAME` | Device name used in health check responses |
| `ENVIRONMENT` | Set to `raspberry_pi` for real GPIO, anything else for mock |
| `API_URL` | Full URL to the REST API (e.g. `http://192.168.x.x:5001`) |

## Tests

There are no automated tests. CI runs flake8 to lint the Python code. The service can be tested by sending MQTT messages to `irrigation/request` and watching the Docker logs.

```bash
docker compose logs -f
```

## GPIO pin mapping (BCM)

| Zone | GPIO | Zone | GPIO |
|------|------|------|------|
| 1    | 2    | 11   | 5    |
| 2    | 3    | 12   | 6    |
| 3    | 4    | 13   | 14   |
| 4    | 17   | 14   | 15   |
| 5    | 27   | 15   | 18   |
| 6    | 26   | 16   | 23   |
| 7    | 10   | 17   | 21   |
| 8    | 9    | 18   | 25   |
| 9    | 11   | 19   | 8    |
| 10   | 0    | 20   | 7    |

Relays are **active LOW** — GPIO LOW = relay on, GPIO HIGH = relay off.

## MQTT topics

| Direction | Topic | Payload |
|---|---|---|
| Subscribe | `irrigation/request` | `{ duration, zone, priority, subzones? }` |
| Subscribe | `irrigation/stop` | `{ id }` |
| Subscribe | `irrigation/stopAll` | Any |
| Subscribe | `irrigation/flow` | `{ sensor, pulse_count }` |
| Subscribe | `healthcheck/request` | Any |
| Publish | `irrigation/currentState` | Zone state array (retained) |
| Publish | `irrigation/queue` | Serialized priority queue (retained) |
| Publish | `irrigation/liveFlow` | `{ id, litres }` per second during active run |
| Publish | `healthcheck/response` | `{ device: "<device_name>" }` |

## How I work on it

Changes start as specs in `docs/specs/`. Claude Code implements them on a branch and I review and merge every pull request.
