from game import Game
import asyncio
import websockets
import json

async def handler(websocket):
    game = Game()
    # receiving data
    async for message in websocket:
        event = json.loads(message)
        if event["type"] == "start":
            async for state in game.rungame():
                # print(json.dumps(state))
                await websocket.send(json.dumps(state))
        # print(message)

        

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())