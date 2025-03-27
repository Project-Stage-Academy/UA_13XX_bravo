from mongoengine import Document, ListField, StringField, IntField, DateTimeField, ReferenceField
from datetime import datetime

class Room(Document):
    participants = ListField(IntField(), required=True)  
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

class Message(Document):
    room = ReferenceField(Room, reverse_delete_rule=2) 
    sender_id = IntField(required=True)  
    text = StringField(required=True)
    timestamp = DateTimeField(default=datetime.now)
