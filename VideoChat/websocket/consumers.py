import json
import random
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django_redis import get_redis_connection

logger = logging.getLogger("video_call_consumer")


@database_sync_to_async
def get_authenticated_user(scope):
    user = scope.get("user")
    return user if user and user.is_authenticated else None


class VideoCallConsumer(AsyncWebsocketConsumer):
   async def connect(self):
    self.user = await get_authenticated_user(self.scope)

    if not self.user:
        logger.warning("Unauthenticated user tried to connect.")
        await self.close()
        return

    self.username = self.user.username
    self.room_group_name = f"video_{self.username}"

    await self.accept()

    # پس از accept کانکشن، اکنون channel_name در دسترس است
    if not hasattr(self, "channel_name"):
        logger.error(f"[ERROR] No channel_name for {self.username}")
        await self.close()
        return

    self.redis_conn = get_redis_connection("default")
    self.redis_conn.hset("online_users", self.username, self.channel_name)
    self.redis_conn.sadd("available_for_random_call", self.username)

    logger.info(f"[CONNECTED] {self.username} -> {self.channel_name}")

    await self.channel_layer.group_add(
        self.room_group_name,
        self.channel_name
    )


    async def disconnect(self, close_code):
        if hasattr(self, "username"):
            self.redis_conn.hdel("online_users", self.username)
            self.redis_conn.srem("available_for_random_call", self.username)

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"[DISCONNECTED] {self.username} left. Code: {close_code}")

    async def receive(self, text_data):
        if not self.user or not self.user.is_authenticated:
            logger.warning("Message received from unauthenticated user.")
            return

        try:
            data = json.loads(text_data)
            msg_type = data.get("type")
            target_username = data.get("target")

            if msg_type == "get_random_user":
                random_user = await self._get_random_user(self.username)
                await self.send(text_data=json.dumps({
                    "type": "random_user",
                    "target": random_user
                }))
                logger.info(f"[RANDOM USER] {self.username} -> {random_user}")
                return

            if target_username:
                target_channel = self.redis_conn.hget("online_users", target_username)
                if target_channel:
                    target_channel = target_channel.decode()
                    message_to_send = data.copy()
                    message_to_send["sender"] = self.username

                    logger.info(f"[FORWARD] {self.username} -> {target_username}")

                    await self.channel_layer.send(
                        target_channel,
                        {
                            "type": "send.sdp",
                            "data": message_to_send
                        }
                    )
                else:
                    logger.warning(f"[OFFLINE] {target_username} not online")
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": f"User {target_username} is not online."
                    }))
            else:
                logger.warning(f"[INVALID] No target specified by {self.username}")

        except json.JSONDecodeError:
            logger.error(f"[JSON ERROR] Invalid JSON: {text_data}")
        except Exception as e:
            logger.exception(f"[ERROR] Exception in receive(): {e}")

    async def send_sdp(self, event):
        try:
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            logger.exception(f"[ERROR] Failed to send SDP message: {e}")

    @database_sync_to_async
    def _get_random_user(self, exclude_username):
        users = self.redis_conn.smembers("available_for_random_call")
        users = [u.decode() for u in users if u.decode() != exclude_username]
        return random.choice(users) if users else None
