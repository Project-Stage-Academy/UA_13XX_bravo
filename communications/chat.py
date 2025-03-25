from channels.generic.websocket import AsyncWebsocketConsumer
import json


class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected!"}))

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"echo": text_data}, ensure_ascii=False))
