import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)
online_users = set()

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = f"video_{self.username}"

        online_users.add(self.username)
        logger.info(f"[Connect] User connected: {self.username}")
        logger.debug(f"[Connect] Current online users: {online_users}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "connection_success",
            "message": f"Connected as {self.username}"
        }))

    async def disconnect(self, close_code):
        logger.info(f"[Disconnect] User disconnected: {self.username}, Code: {close_code}")
        online_users.discard(self.username)
        logger.debug(f"[Disconnect] Current online users: {online_users}")

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            logger.debug(f"[Receive] Raw data: {text_data}")
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            logger.error(f"[Error] JSON Decode Error: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
            return

        event_type = data.get("type")
        logger.info(f"[Receive] Received event type: {event_type} from {self.username}")

        if event_type == "get_random_user":
            target = self.get_random_user(exclude=self.username)
            logger.info(f"[Random Match] {self.username} matched with {target}")
            await self.send(text_data=json.dumps({
                "type": "random_user",
                "target": target
            }))
        else:
            target = data.get("target")
            if not target:
                logger.warning(f"[Warning] Missing target in message from {self.username}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Target username not specified"
                }))
                return

            if target not in online_users:
                logger.warning(f"[Warning] Target user {target} not online. Message from {self.username}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"Target user {target} is not online"
                }))
                return

            logger.info(f"[Forward] From {self.username} → To {target} | Data: {data}")
            await self.channel_layer.group_send(
                f"video_{target}",
                {
                    "type": "send.sdp",
                    "data": data
                }
            )

    async def send_sdp(self, event):
        logger.debug(f"[Send SDP] Sending SDP data to {self.username}: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))

    def get_random_user(self, exclude):
        candidates = list(online_users - {exclude})
        logger.debug(f"[Random User] Candidates for {exclude}: {candidates}")
        return random.choice(candidates) if candidates else None