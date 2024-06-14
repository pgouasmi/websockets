import asyncio
import websockets
import json

async def receive_messages(websocket):
    print("Receiving messages")
    async for message in websocket:
        print(f"Received: {message}")

async def send_message():
    uri = "ws://localhost:8001"
    async with websockets.connect(uri) as websocket:
        # Send the initial message
        message = {"type": "start", "data": "Hello, World!"}
        await websocket.send(json.dumps(message))

        # Receive and print messages
        async for message in websocket:
            print(f"Received message: {message}")

asyncio.run(send_message())