import asyncio
import json
import os

import websockets
import requests

from model.Incident import Incident, IncidentLevel

clients = set()
IP = "0.0.0.0"
PORT = 2277

UPLOAD_FOLDER = 'database'
INCIDENT_FILE_NAME = "incident.json"
INCIDENT_FILE = os.path.join(UPLOAD_FOLDER, INCIDENT_FILE_NAME)

DOMAIN = "http://0.0.0.0:5044/"
END_POINT = "upload"
UPLOAD_TO_LLM_URL = "{}{}".format(DOMAIN, END_POINT)

async def broadcast(message, sender):
    for client in clients:
        if client != sender:
            await client.send(message)

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            if "danger" in message.lower():
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(send_dangerous_report(message))
                    tg.create_task(broadcast(message, websocket))
            else:
                await broadcast(message, websocket)
    except* Exception as ex:
        print(ex.exceptions)
    finally:
        clients.remove(websocket)


async def send_dangerous_report(message: str):
    print("send_dangerous_report {}".format(message))
    parts = message.split(';')
    content = parts[-1]
    incident = Incident(details=content, status=IncidentLevel.THREAT)
    incident_json = json.loads(incident.to_json())
    with open(INCIDENT_FILE, "w+") as f:
        json.dump(incident_json, f, indent=4)
    payload = {'source': 'incident_activity'}
    headers = {}
    with open(INCIDENT_FILE, "rb") as f:
        response = requests.post(UPLOAD_TO_LLM_URL, headers=headers,
                                 files={'file': (INCIDENT_FILE_NAME, f)},
                                 data=payload
                                 )
    print(response)

async def connect_to_server():
    uri = "ws://{}:{}".format(IP, PORT)
    async with websockets.connect(uri) as websocket:
        return websocket

start_server = websockets.serve(handler, IP, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
