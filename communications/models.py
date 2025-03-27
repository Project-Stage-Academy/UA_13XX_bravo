from mongoengine import Document, StringField, IntField

class ChatRoom(Document):
    company_id_1 = IntField()
    company_id_2 = IntField()
    mongo_room_id = StringField(max_length=255)