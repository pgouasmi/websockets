# from game import Game
# import asyncio
# import websockets
# import json

# class GameOverException(Exception):
#     pass

# async def handler(websocket):
#     game = Game()
#     # receiving data
#     async for message in websocket:
#         event = json.loads(message)
#         if event["type"] == "start":
#             async for state in game.rungame():
#                 state = json.loads(state)
#                 await websocket.send(json.dumps(state))
#                 if state["type"] == "gameover":
#                     game.quit()
#                     raise GameOverException()
#         # print(message)

        

# async def main():
#     try:
#         async with websockets.serve(handler, "", 8001):
#             await asyncio.Future()  # run forever
#     except GameOverException:
#         print("Game Over")


# if __name__ == "__main__":
#     asyncio.run(main())


from game import Game
import asyncio
import websockets
import json

game_over = asyncio.Queue()

async def handler(websocket):
    game = Game()
    # receiving data
    async for message in websocket:
        event = json.loads(message)
        if event["type"] == "start":
            game.handleArguments(event)
            async for state in game.rungame():
                state = json.loads(state)
                await websocket.send(json.dumps(state))
                if state["type"] == "gameover":
                    game.quit()
                    await game_over.put('gameover')
                    return

async def main():
    server = await websockets.serve(handler, "", 8001)
    await game_over.get()  # wait for 'gameover'
    server.close()
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())