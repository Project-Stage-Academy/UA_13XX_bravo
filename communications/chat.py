from channels.generic.websocket import AsyncWebsocketConsumer
import json
from communications.mongo_models import Room, Message
from datetime import datetime
from django.utils.timezone import now

class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        #питання чи робити канал чату для групи інвесторів з стартапом чи залишити чат тільки між інвестором і стартапом?
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(json.dumps({"message": "Connected!"}))

    #незнаю чи робити видалення чату після кінця disconnect() , чи це зайве???
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        #load
        data = json.loads(text_data)
        message = data["message"]
        sender_id = data["sender_id"]

        # save
        room = Room.objects.get(id=self.room_id)
        new_message = Message(room=room, sender_id=sender_id, text=message, timestamp=now())
        new_message.save()

        # group_send
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id
            }
        )

    # send
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
