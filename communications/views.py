from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatRoom
from .mongo_models import Room
from .serializers import ChatRoomSerializer

class CreateChatRoomView(APIView):
    def post(self, request, *args, **kwargs):
        company_1 = request.data.get("company_id_1")
        company_2 = request.data.get("company_id_2")
        
        mongo_room = Room.objects.create(participants=[company_1, company_2])

        chat_room = ChatRoom.objects.create(
            company_id_1=company_1,
            company_id_2=company_2,
            mongo_room_id=str(mongo_room.id) 
        )

        return Response({"room_id": chat_room.mongo_room_id}, status=201)
