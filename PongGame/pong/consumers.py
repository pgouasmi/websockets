import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("accpted socket")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"data: {data}")
        # Logique pour gérer les messages reçus
        await self.send(text_data=json.dumps({
            'message': 'pong'
        }))
