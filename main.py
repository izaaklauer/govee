import os
import requests
import logging
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def get_govee_devices(api_key):
    """
    Return a list of devices from the Govee API.
    """
    url = "https://openapi.api.govee.com/router/api/v1/user/devices"
    headers = {
        "Govee-API-Key": api_key,
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    # data should look like {"code":200,"message":"success","data":[{...}, {...}]}
    return data.get("data", [])


def get_sensor_data(api_key, sku, device_id):
    """
    Return the temperature and humidity from Govee for a single device.
    """
    url = "https://openapi.api.govee.com/router/api/v1/device/state"
    headers = {
        "Govee-API-Key": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "requestId": "govee-req-1",
        "payload": {
            "sku": sku,
            "device": device_id
        }
    }

    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    # data should look like:
    # {
    #   "requestId": "...",
    #   "msg": "success",
    #   "code": 200,
    #   "payload": {
    #       "sku": "H5100",
    #       "device": "...",
    #       "capabilities": [
    #           {"type":"devices.capabilities.property","instance":"sensorTemperature","state":{"value":63.14}},
    #           {"type":"devices.capabilities.property","instance":"sensorHumidity","state":{"value":{"currentHumidity":48}}}
    #       ]
    #   }
    # }
    capabilities = data.get("payload", {}).get("capabilities", [])

    temperature = None
    humidity = None

    for cap in capabilities:
        instance = cap.get("instance")
        state_value = cap.get("state", {}).get("value")

        if instance == "sensorTemperature":
            # example: state_value = 63.14
            temperature = state_value
        elif instance == "sensorHumidity":
            # example: state_value = {"currentHumidity": 48}
            if isinstance(state_value, dict):
                humidity = state_value.get("currentHumidity")
            else:
                humidity = state_value

    return temperature, humidity


def write_to_influx(influx_client, bucket, org, measurement, tags, fields):
    """
    Write a measurement with tags and fields to InfluxDB.
    """
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    point = (
        Point(measurement)
        .tag("device", tags.get("device", "unknown"))
        .tag("deviceName", tags.get("deviceName", "unknown"))
        .field("temperature2", int(fields.get("temperature")))
        .field("humidity2", int(fields.get("humidity")))
        .time(time.time_ns(), WritePrecision.NS)  # current time
    )

    write_api.write(bucket=bucket, org=org, record=point)


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # -- Govee Configuration --
    govee_api_key = os.getenv("GOVEE_API_KEY", "<YOUR-GOVEE-API-KEY>")

    # -- InfluxDB Configuration --
    influx_url = os.getenv("INFLUX_ADDR", "http://localhost:8086")
    influx_token = os.getenv("INFLUX_TOKEN", "<YOUR-INFLUX-TOKEN>")
    influx_org = os.getenv("INFLUX_ORG", "<YOUR-ORG>")
    influx_bucket = os.getenv("INFLUX_BUCKET", "<YOUR-BUCKET>")

    # Initialize Influx client
    influx_client = InfluxDBClient(
        url=influx_url,
        token=influx_token,
        org=influx_org
    )

    # 1. Get all Govee devices
    devices = get_govee_devices(govee_api_key)
    logger.info("Found %d devices from Govee.", len(devices))

    # 2. For each device, retrieve temperature and humidity and write to Influx
    for device_info in devices:
        sku = device_info.get("sku")
        device_id = device_info.get("device")
        device_name = device_info.get("deviceName", "unknown")

        temperature, humidity = get_sensor_data(govee_api_key, sku, device_id)

        if temperature is not None and humidity is not None:
            logger.info("Device %s (%s): Temp=%.2f, Humidity=%.2f",
                        device_name, device_id, temperature, humidity)

            # 3. Write to InfluxDB
            tags = {
                "device": device_id,
                "deviceName": device_name
            }
            fields = {
                "temperature": temperature,
                "humidity": humidity
            }

            write_to_influx(
                influx_client=influx_client,
                bucket=influx_bucket,
                org=influx_org,
                measurement="govee_sensors",
                tags=tags,
                fields=fields
            )
        else:
            logger.warning("Could not retrieve temperature/humidity for %s (%s).", device_name, device_id)


if __name__ == "__main__":
    logging.info("Starting Govee InfluxDB scraping script...")
    while True:
        main()
        time.sleep(60)
