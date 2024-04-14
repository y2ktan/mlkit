import asyncio
import websockets

clients = set()
IP = "0.0.0.0"
PORT = 2277

async def broadcast(message, sender):
    for client in clients:
        if client != sender:
            await client.send(message)

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await broadcast(message, websocket)
    finally:
        clients.remove(websocket)

async def connect_to_server():
    uri = "ws://{}:{}".format(IP, PORT)
    async with websockets.connect(uri) as websocket:
        return websocket

start_server = websockets.serve(handler, IP, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
