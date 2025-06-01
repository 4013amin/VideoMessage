import json
import random
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import get_user
from django_redis import get_redis_connection

logger = logging.getLogger("video_call")

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = await get_user(self.scope)
        if not user.is_authenticated:
            await self.close()
            logger.warning("اتصال رد شد: کاربر احراز هویت نشده است.")
            return

        self.username = user.username
        self.room_group_name = f"video_{self.username}"

        redis = get_redis_connection("default")
        redis.hset("online_users", self.username, self.channel_name)

        logger.info(f"[CONNECT] User connected: {self.username} => {self.channel_name}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"[ACCEPT] WebSocket accepted for {self.username}")

    async def disconnect(self, close_code):
        redis = get_redis_connection("default")
        if redis.hexists("online_users", self.username):
            redis.hdel("online_users", self.username)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"[DISCONNECT] Removing user: {self.username}")

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
                redis = get_redis_connection("default")
                if redis.hexists("online_users", target):
                    data["sender"] = self.username
                    logger.info(f"[FORWARD] {self.username} -> {target}: {msg_type}")
                    await self.channel_layer.send(redis.hget("online_users", target).decode(), {
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
        redis = get_redis_connection("default")
        candidates = [u.decode() for u in redis.hkeys("online_users") if u.decode() != exclude]
        return random.choice(candidates) if candidates else None