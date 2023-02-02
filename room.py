import json
import asyncio
import sys
import time
import logging

from wotpy.wot.servient import Servient
from wotpy.wot.wot import WoT

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

LAMP_CAT_PORT = 9100
LIGH_CAT_PORT = 9200
DETE_CAT_PORT = 9300

async def main():
    wot = WoT(servient=Servient())
    
    presence = False
    light = 0.0

    LOGGER.info("Connecting to devices...")
    if sys.platform == 'win32':
        # If running locally.
        lamp_thing = await wot.consume_from_url(f'http://127.0.0.1:{LAMP_CAT_PORT}/smart-lamp-9454761a-15d8-6551-9c09-086f698e6102')
        light_sensor_thing = await wot.consume_from_url(f'http://127.0.0.1:{LIGH_CAT_PORT}/sensor-light-de085598-f7f4-fbc1-6ea2-522e94c6c44d')
        detection_sensor_thing = await wot.consume_from_url(f'http://127.0.0.1:{DETE_CAT_PORT}/sensor-detect-de085598-f7f4-fbc1-6ea2-522e94c6c44d')
    else:
        # If running on cloud.
        lamp_thing = await wot.consume_from_url(f'https://lamp-319o.onrender.com:{LAMP_CAT_PORT}/smart-lamp-9454761a-15d8-6551-9c09-086f698e6102')
        light_sensor_thing = await wot.consume_from_url(f'https://light-319o.onrender.com:{LIGH_CAT_PORT}/sensor-light-de085598-f7f4-fbc1-6ea2-522e94c6c44d')
        detection_sensor_thing = await wot.consume_from_url(f'https://detect-319o.onrender.com:{DETE_CAT_PORT}/sensor-detect-de085598-f7f4-fbc1-6ea2-522e94c6c44d')
    LOGGER.info("Connected to devices.")

    # Subscribing to lamp state changing.
    lamp_thing.events['stateChanged'].subscribe(
        on_next=lambda data: LOGGER.info(f'Value changed for lamp: {data}'),
        on_completed=LOGGER.info('Subscribed to lamp state'),
        on_error=lambda error: LOGGER.info(f'Error subscribing to lamp state: {error}')
    )
    
    # Logic control of the lamp based on sensors values.
    def switch_light():
        global light
        global presence
        print("switch_light")
        if(presence and light < 0.2):
            lamp_thing.invoke_action('on')
            return
        lamp_thing.invoke_action('off')

    # Subscribe to light sensor data.
    def update_light(data):
        print(f"New light level: {data}")
        global light
        light = float(data)
        switch_light()
    light_sensor_thing.events['lightChanged'].subscribe(
        on_next=lambda data: update_light(data),
        on_completed=LOGGER.info("Subscribed to light sensor."),
        on_error=lambda error: LOGGER.info(f'Error subscribing to light sensor: {error}')
    )

    # Subscribe to presence sensor data.
    def update_presence(data):
        print(f"Detection toggled: {data}")
        global presence
        presence = bool(data)
        switch_light()
    detection_sensor_thing.events['presenceChanged'].subscribe(
        on_next=lambda data: update_presence(data),
        on_completed=LOGGER.info("Subscribed to presence sensor."),
        on_error=lambda error: LOGGER.info(f'Error subscribing to presence sensor: {error}')
    )

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()