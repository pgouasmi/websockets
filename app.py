import asyncio
import time

import websockets
import json
import signal
from game import Game

game_over = asyncio.Event()
resume_on_goal = asyncio.Event()
game_is_initialized = asyncio.Event()
ai_is_initialized = asyncio.Event()
game = None


async def listen_for_messages(websocket, start_event):
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
            game.resume_on_goal()
            generating.set()
        await asyncio.sleep(0.00000001)


async def handleFrontInput(event):
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


async def generate_states(websocket, start_event):
    print("Generating states")
    await ai_is_initialized.wait()
    await start_event.wait()
    async for state in game.rungame():
        print(f"new state:{state}")
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
        ai_data = game.getGameState()
        await websocket.send(state)
        await websocket.send(json.dumps(ai_data))
        await asyncio.sleep(0.00000001)

def handle_ai_message(message):
    if message["type"] == "setup":
        ai_is_initialized.set()
    if message["type"] == "move":
        if message["direction"] == "up":
            game.paddle2.move(game.height, up=True)
        elif message["direction"] == "down":
            game.paddle2.move(game.height, up=False)
        else:
            print(f"Unknown direction: {message['direction']}")

async def send_ai_setup_instructions(websocket):
    print(f"Sending AI setup instructions")
    ai_data = {
        "type": "setup",
        "width": game.width,
        "height": game.height,
        "paddle_width": game.paddle2.width,
        "paddle_height": game.paddle2.height,
        "loading": game.LOADING,
    }
    if game.RUNNING_AI is False:
        ai_data["difficulty"] = 0
    else:
        ai_data["difficulty"] = game.DIFFICULTY
    print(f"Sending AI setup instructions: {ai_data}")
    await websocket.send(json.dumps(ai_data))
    await asyncio.sleep(0.00000001)


async def handlerAI(websocket):
    print("AI interface started")
    await game_is_initialized.wait()
    print("Game is initialized")
    if game.RUNNING_AI is False:
        websocket.close()
        ai_is_initialized.set()
        return
    await send_ai_setup_instructions(websocket)
    last_timestamp = 0
    game_state = None
    async for message in websocket:
        print(f"new message received from AI: {message}")
        handle_ai_message(json.loads(message))
        if time.time() - last_timestamp < 1 and game is not None:
            game_state = game.getGameState()
        websocket.send(json.dumps(game_state))
        await asyncio.sleep(0.00000001)




async def handler(websocket):
    global game
    game = Game()
    game_is_initialized.set()
    if game.RUNNING_AI is False:
        ai_is_initialized.set()
    def signal_handler():
        print("Signal SIGINT reçu, arrêt du jeu...")
        game.quit()
        game_over.set()
        return True

    # Enregistrer le gestionnaire de signaux
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)

    start_event = asyncio.Event()
    listener_task = asyncio.create_task(listen_for_messages(websocket, start_event))
    state_generator_task = asyncio.create_task(generate_states(websocket, start_event))

    # Attendre l'événement "start" avant de démarrer la génération des états
    # await start_event.wait()
    await asyncio.gather(listener_task, state_generator_task)
    if game_over.is_set():
        return

    done, pending = await asyncio.wait(
        [listener_task, state_generator_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()  # Annuler les tâches en attente si une tâche se termine
    loop.remove_signal_handler(signal.SIGINT)

async def main():

    server = await websockets.serve(handler, "", 8001)
    print("before server ai")
    server_ai = await websockets.serve(handlerAI, "", 7777)
    await game_over.wait()  # Attendre le signal de fin de jeu
    server.close()
    server_ai.close()
    # await server.close()
    # await server_ai.close()


if __name__ == "__main__":
    asyncio.run(main())

