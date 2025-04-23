import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer


from django.db.utils import IntegrityError
from communications.models import ChatRoom
from companies.models import CompanyProfile, CompanyType
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class RoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        error = self.scope.get("auth_error")  # from middlware
        if error:
            await self.accept()
            await self.send_error(error)
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        logger.debug(f"[WS] Connected to group chat_{self.room_id}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_notification(self, event):
        logger.debug(f"[WS] Sending notification to WS: {event['notification']}")
        await self.send_json(event["notification"])


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """
        Handles WebSocket connection and creates the chat room if it doesn't exist.
        Returns detailed error info to the client if validation fails.
        """

        error = self.scope.get("auth_error")  # from middlware
        if error:
            await self.accept()
            await self.send_error(error)
            return

        await self.accept()  # Accept first to allow sending error messages
        await self.set_params()

        error = await self.validate()
        if error:
            await self.send_error(error)
            return

        self.room = await self.get_or_create_chat_room(self.company1, self.company2)
        self.room_group_name = f"chat_{self.room.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def set_params(self):
        kwargs = self.scope["url_route"]["kwargs"]
        self.user = self.scope["user"]
        self.company1 = await self.get_company_by_id(kwargs["company_id_1"])
        self.company2 = await self.get_company_by_id(kwargs["company_id_2"])

    async def validate(self):
        """
        Validate the WebSocket connection request.

        Checks if the user is authenticated, verifies the existence of companies,
        ensures exactly one company is a STARTUP, and sets company2 as the STARTUP.

        Returns:
            str: Error message if validation fails, otherwise None.
        """
        error = None

        # Check user presence and authentication
        if not self.user:
            error = "User information is missing."
        elif not self.user.is_authenticated:
            error = f"{self.user} is not authenticated."

        # Check both companies exist
        elif not self.company1 or not self.company2:
            error = "One or both companies are missing."

        # Ensure exactly one company is a STARTUP
        else:
            is_startup_1 = self.company1.type == CompanyType.STARTUP
            is_startup_2 = self.company2.type == CompanyType.STARTUP

            if is_startup_1 and is_startup_2:
                error = "Both companies are STARTUPs — only one is allowed."
            elif not is_startup_1 and not is_startup_2:
                error = "Neither company is a STARTUP — one must be."

            # Swap so that company2 is always the STARTUP
            elif is_startup_1 and not is_startup_2:
                self.company1, self.company2 = self.company2, self.company1

        return error

    async def get_company_by_id(self, company_id):
        try:
            return await sync_to_async(CompanyProfile.objects.get)(id=company_id)
        except CompanyProfile.DoesNotExist:
            return None

    async def get_or_create_chat_room(self, company1, company2):
        """
        Creates or retrieves a chat room between two users.
        """
        try:
            room, _ = await sync_to_async(ChatRoom.objects.get_or_create)(
                company_id_1=company1, company_id_2=company2
            )
            return room
        except IntegrityError:
            # In case of conflicts, retrieve the existing room
            return await sync_to_async(ChatRoom.objects.get)(
                company_id_1=company1, company_id_2=company2
            )

    async def disconnect(self, close_code):
        """
        Disconnects the user from the chat group upon exit.
        """
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        """
        Handles receiving a message and saves it in the database.
        """
        if not hasattr(self, "room"):
            await self.send_error("Chat room not initialized.")
            return
        data = json.loads(text_data)
        message_content = data.get("message")

        # Save the message to the database
        await self.save_message(
            self.room, self.company1, self.company2, message_content
        )

        # Send the message to all participants in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "sender": self.user.email,
            },
        )

    async def send_error(self, message: str, code: int = 4001):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "message": message,
                }
            )
        )
        await self.close(code=code)

    async def chat_message(self, event):
        """
        Sends a message to the WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                }
            )
        )

    async def save_message(self, room, sender, receiver, content):
        """
        Saves a message in the database.
        """
        pass
