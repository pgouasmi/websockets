import asyncio
import websockets
import json
from game import Game

game_over = asyncio.Queue()


async def listen_for_messages(websocket, game, start_event):
    async for message in websocket:
        # print("New message received")
        event = json.loads(message)
        if event["type"] == "keyDown":
            await handleFrontInput(game, event)
        elif event["type"] == "start":
            # Signal pour démarrer la génération des états du jeu
            start_event.set()
        await asyncio.sleep(0.00000001)


async def handleFrontInput(game, event):
    print(event)
    if event["event"] == "pause":
        game.pause = not game.pause
    elif event["event"] == "player1Up":
        for i in range(10):
            game.paddle1.move(game.height, up=True)
    elif event["event"] == "player1Down":
        for i in range(10):
            game.paddle1.move(game.height, up=False)


async def generate_states(game, websocket, start_event):
    await start_event.wait()
    async for state in game.rungame():
        # print("new state")
        if game.pause == False:
            state_dict = json.loads(state)
            if state_dict["type"] == "gameover":
                game.quit()
                await game_over.put(state_dict)
                return
            state = json.dumps(json.loads(state))
            await websocket.send(state)
        await asyncio.sleep(0.00000001)


async def handler(websocket):
    game = Game()
    start_event = asyncio.Event()
    listener_task = asyncio.create_task(listen_for_messages(websocket, game, start_event))
    state_generator_task = asyncio.create_task(generate_states(game, websocket, start_event))

    # Attendre l'événement "start" avant de démarrer la génération des états
    # await start_event.wait()
    await asyncio.gather(listener_task, state_generator_task)

    done, pending = await asyncio.wait(
        [listener_task, state_generator_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()  # Annuler les tâches en attente si une tâche se termine


async def main():
    server = await websockets.serve(handler, "", 8001)
    await game_over.get()  # Attendre le signal de fin de jeu
    # server.close()
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())

