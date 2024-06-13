import asyncio
import websockets
import json

# async def send_message():
#     uri = "ws://localhost:8001"
#     async with websockets.connect(uri) as websocket:
#         flag = 0
#         while True:
#             if flag == 0:
#                 message = {"type": "start", "data": "Hello, World!"}
#                 await websocket.send(json.dumps(message))
#             else:
#                 message = {"type": "OK", "data": "Hello, World!"}
#             flag = 1
#             try:
#                 response = await asyncio.wait_for(websocket.recv(), timeout=10)
#                 print(f"Received: {response}")
#             except asyncio.TimeoutError:
#                 # No message received, continue the loop
#                 pass

async def receive_messages(websocket):
    async for message in websocket:
        print(f"Received: {message}")


async def send_message():
    uri = "ws://localhost:8001"
    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.create_task(receive_messages(websocket))
        try:
            flag = 0
            while True:
                if flag == 0:
                    message = {"type": "start", "data": "Hello, World!"}
                    await websocket.send(json.dumps(message))
                else:
                    message = {"type": "OK", "data": "Hello, World!"}
                flag = 1
        except Exception as e:
            print(f"Error: {e}")
        finally:
            receive_task.cancel()

    try:
        await receive_task
    except asyncio.CancelledError:
        pass
 

asyncio.run(send_message())