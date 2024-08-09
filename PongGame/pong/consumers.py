import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import Game

class PongConsumer(AsyncWebsocketConsumer):
    game = None
    game_over = asyncio.Event()
    resume_on_goal = asyncio.Event()
    game_is_initialized = asyncio.Event()
    ai_is_initialized = asyncio.Event()
    start_event = asyncio.Event()

    async def connect(self):
        # Accepter la connexion WebSocket
        await self.accept()
        self.game = Game()
        self.game_is_initialized.set()
        print("game is initialized")
        if self.game.RUNNING_AI is False:
            self.ai_is_initialized.set()

        # Démarrer les tâches asynchrones
        await self.channel_layer.group_add("pong", self.channel_name)
        asyncio.create_task(self.generate_states())

    async def disconnect(self, close_code):
        # Déconnecter WebSocket proprement
        await self.channel_layer.group_discard("pong", self.channel_name)

    async def receive(self, text_data):
        # Traiter les messages reçus du client
        event = json.loads(text_data)
        print(f"received event: {event}")
        if event["type"] == "keyDown":
            await self.handle_front_input(event)
        elif event["type"] == "start":
            self.start_event.set()
            self.resume_on_goal.set()
        elif event["type"] == "resumeOnGoal":
            self.resume_on_goal.clear()
            await self.game.resume_on_goal()
            self.resume_on_goal.set()

    async def handle_front_input(self, event):
        if event["event"] == "pause":
            self.game.pause = not self.game.pause
        elif event["event"] == "player1Up":
            for _ in range(10):
                self.game.paddle1.move(self.game.height, up=True)
        elif event["event"] == "player1Down":
            for _ in range(10):
                self.game.paddle1.move(self.game.height, up=False)

        elif event["event"] == "player2Up":
            for _ in range(10):
                self.game.paddle2.move(self.game.height, up=True)
        elif event["event"] == "player2Down":
            for _ in range(10):
                self.game.paddle2.move(self.game.height, up=False)

        elif event["event"] == "reset":
            self.game.ball.reset(self.game.ball.x)
            self.game.state = self.game.getGameState()
            self.game.lastSentInfos = 0

    async def generate_states(self):
        print("in generate states")
        await self.ai_is_initialized.wait()
        await self.start_event.wait()
        print("state gen set")
        async for state in self.game.rungame():
            await self.resume_on_goal.wait()
            state_dict = json.loads(state)
            if state_dict["type"] == "gameover":
                self.game.quit()
                self.game_over.set()
                break
            await self.send(text_data=json.dumps(state_dict))
            await asyncio.sleep(0.00000001)

    async def listen_for_messages(self):
        pass  # Traite les messages via la méthode `receive`
