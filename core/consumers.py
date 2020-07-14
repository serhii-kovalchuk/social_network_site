import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from core.models import Like
from core.forms import LikeForm


class LikeConsumer(AsyncWebsocketConsumer):
    form_class = LikeForm

    async def connect(self):
        self.room_group_name = 'ws_posts_like'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)

        try:
            event = data['event']
            user = data['user']
            post = data['post']
        except KeyError:
            print("Invalid data format", data)
            return

        if event == 'add_like':
            form = self.form_class(data=data)
            if form.is_valid():
                sync_to_async(form.save())
            else:
                print("Invalid data format, errors:", form.errors.as_json())
                return

        elif event == 'remove_like':
            try:
                # get() could be better but it is unclear can user like multiple times or not
                sync_to_async(Like.objects.filter(user_id=user, post_id=post).last().delete())
            except Like.DoesNotExist:
                print(f"Like object with user_id = {user} and post_id = {post} does not exist")
                return

        else:
            print("Invalid event name", event)
            return

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_message',
                'data': data,
            }
        )

    # Receive message from room group
    async def new_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))


class BotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'ws_bot_%s' % self.user_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def message_from_bot(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


