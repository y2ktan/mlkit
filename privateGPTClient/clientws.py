import asyncio
import websockets

clients = set()

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

start_server = websockets.serve(handler, "0.0.0.0", 2277)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
