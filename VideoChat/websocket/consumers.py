import json
import random
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("video_call")
online_users = {}

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f"video_{self.username}"
        online_users[self.username] = self.channel_name

        logger.info(f"[CONNECT] User connected: {self.username} => {self.channel_name}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.username in online_users:
            logger.info(f"[DISCONNECT] Removing user: {self.username}")
            del online_users[self.username]
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.debug(f"[RECEIVE] From {self.username}: {text_data}")
        try:
            data = json.loads(text_data)
            msg_type = data.get("type")

            if msg_type == "get_random_user":
                target = self.get_random_user(self.username)
                logger.info(f"[RANDOM USER] Selected for {self.username}: {target}")
                await self.send(text_data=json.dumps({
                    "type": "random_user",
                    "target": target
                }))
            else:
                target = data.get("target")
                if target in online_users:
                    data["sender"] = self.username
                    logger.info(f"[FORWARD] {self.username} -> {target}: {msg_type}")
                    await self.channel_layer.send(online_users[target], {
                        "type": "send.sdp",
                        "data": data
                    })
                else:
                    logger.warning(f"[ERROR] Target user '{target}' not online.")
        except Exception as e:
            logger.error(f"[ERROR] Failed to process message: {e}")

    async def send_sdp(self, event):
        logger.debug(f"[SEND_SDP] To {self.username}: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))

    def get_random_user(self, exclude):
        candidates = [u for u in online_users if u != exclude]
        return random.choice(candidates) if candidates else None
