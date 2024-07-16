import asyncio
import websockets
import json
import signal
from game import Game

game_over = asyncio.Event()
generating = asyncio.Event()

async def listen_for_messages(websocket, game, start_event):
    async for message in websocket:
        # print(f"New message received {message}")
        event = json.loads(message)
        if event["type"] == "keyDown":
            await handleFrontInput(game, event)
        elif event["type"] == "start":
            # Signal pour démarrer la génération des états du jeu
            start_event.set()
            generating.set()
        elif event["type"] == "resumeOnGoal":
            await game.resume_on_goal()
            generating.set()
        await asyncio.sleep(0.00000001)


async def handleFrontInput(game, event):
    # print(event)
    if event["event"] == "pause":
        game.pause = not game.pause
    elif event["event"] == "player1Up":
        for i in range(10):
            game.paddle1.move(game.height, up=True)
    elif event["event"] == "player1Down":
        for i in range(10):
            game.paddle1.move(game.height, up=False)
    elif event["event"] == "reset":
        game.ball.reset(game.ball.x)
        game.state = game.getGameState()
        game.lastSentInfos = 0


async def generate_states(game, websocket, start_event):
    await start_event.wait()
    async for state in game.rungame():
        # print("new state")
        # if game.pause == False:
        # print(f"generating: {generating.is_set()}")
        await generating.wait()
        state_dict = json.loads(state)
        if state_dict["goal"] != "None":
            generating.clear()
        if state_dict["type"] == "gameover":
            game.quit()
            await game_over.put(state_dict)
            return
        state = json.dumps(json.loads(state))
        await websocket.send(state)
        await asyncio.sleep(0.00000001)


async def handler(websocket):
    game = Game()

    def signal_handler():
        print("Signal SIGINT reçu, arrêt du jeu...")
        game.quit()
        game_over.set()
        return True

    # Enregistrer le gestionnaire de signaux
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)

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
    loop.remove_signal_handler(signal.SIGINT)

async def main():


    server = await websockets.serve(handler, "", 8001)
    await game_over.wait()  # Attendre le signal de fin de jeu
    server.close()
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())

