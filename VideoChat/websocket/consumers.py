import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = f"video_{self.username}"
        print(f"اتصال WebSocket برای کاربر: {self.username}, گروه: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print(f"قطع اتصال WebSocket برای کاربر: {self.username}, کد: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"دریافت داده از {self.username}: {text_data}")
        data = json.loads(text_data)
        target = data.get("target")

        if target:
            print(f"ارسال داده به هدف: {target}")
            await self.channel_layer.group_send(
                f"video_{target}",
                {
                    "type": "send.sdp",
                    "data": data
                }
            )

    async def send_sdp(self, event):
        print(f"ارسال SDP به {self.username}: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))