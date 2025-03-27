from rest_framework import serializers
from mongoengine import Document, StringField
from mongoengine import connect

class ChatRoom(Document):
    company_id_1 = StringField()
    company_id_2 = StringField()
    mongo_room_id = StringField()

class ChatRoomSerializer(serializers.Serializer):
    company_id_1 = serializers.CharField()
    company_id_2 = serializers.CharField()
    mongo_room_id = serializers.CharField()

    def create(self, validated_data):
        return ChatRoom.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.company_id_1 = validated_data.get('company_id_1', instance.company_id_1)
        instance.company_id_2 = validated_data.get('company_id_2', instance.company_id_2)
        instance.mongo_room_id = validated_data.get('mongo_room_id', instance.mongo_room_id)
        instance.save()
        return instance
