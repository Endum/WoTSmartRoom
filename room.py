import json
import asyncio
import sys

from wotpy.wot.servient import Servient
from wotpy.wot.wot import WoT

async def main():
    wot = WoT(servient=Servient())
    
    print("Connecting to devices...")
    if sys.platform == 'win32':
        # If running locally.
        consumed_thing = await wot.consume_from_url('http://127.0.0.1:9100/smart-lamp-9454761a-15d8-6551-9c09-086f698e6102')
    else:
        # If running on cloud.
        consumed_thing = await wot.consume_from_url('https://lamp-319o.onrender.com:9100/smart-lamp-9454761a-15d8-6551-9c09-086f698e6102')
    print("Connected to devices.")

    lamp_state = await consumed_thing.read_property('state')
    print("Current state of lamp: " + lamp_state)

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()