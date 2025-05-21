import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

online_users = set()


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = f"video_{self.username}"
        online_users.add(self.username)

        print(f"[Connect] {self.username} joined. Online users: {list(online_users)}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        online_users.discard(self.username)

        print(f"[Disconnect] {self.username} left. Code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "get_random_user":
            target = self.get_random_user(exclude=self.username)
            print(f"[Random Match] {self.username} → {target}")
            await self.send(text_data=json.dumps({
                "type": "random_user",
                "target": target
            }))
        else:
            target = data.get("target")
            if target:
                print(f"[Forward] {self.username} → {target}: {data}")
                await self.channel_layer.group_send(
                    f"video_{target}",
                    {
                        "type": "send.sdp",
                        "data": data
                    }
                )

    async def send_sdp(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    def get_random_user(self, exclude):
        candidates = list(online_users - {exclude})
        return random.choice(candidates) if candidates else None
