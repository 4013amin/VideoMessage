import json
import random
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # برای get_user
from django.contrib.auth.models import User # اگر از User پیش‌فرض جنگو استفاده می‌کنید
from django_redis import get_redis_connection

logger = logging.getLogger("video_call_consumer") # نام لاگر را تغییر دادم تا با نام فایل همخوانی داشته باشد

# برای استفاده از get_user در محیط async
@database_sync_to_async
def get_user_async(scope):
    # AuthMiddlewareStack باید user را به scope اضافه کند
    user = scope.get("user")
    if user and user.is_authenticated:
        return user
    return None


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await get_user_async(self.scope)

        if not self.user:
            logger.warning("اتصال رد شد: کاربر احراز هویت نشده است یا کاربر یافت نشد.")
            await self.close()
            return

        self.username = self.user.username # استفاده از username کاربر احراز هویت شده
        # self.room_name = self.scope['url_route']['kwargs']['username'] # این دیگر لازم نیست اگر self.username را از user احراز هویت شده بگیریم
        self.room_group_name = f"video_{self.username}" # هر کاربر در گروه خودش است برای دریافت پیام‌های مستقیم

        redis_conn = get_redis_connection("default")
        # ذخیره نام کانال کاربر برای ارسال مستقیم پیام
        redis_conn.hset("online_users", self.username, self.channel_name)
        # همچنین می‌توان لیستی از کاربران آنلاین را برای انتخاب رندوم نگه داشت
        redis_conn.sadd("available_for_random_call", self.username)


        logger.info(f"[CONNECT] User connected: {self.username} (Channel: {self.channel_name})")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"[ACCEPT] WebSocket accepted for {self.username}")

    async def disconnect(self, close_code):
        if hasattr(self, 'username') and self.username: # چک کنید username ست شده باشد
            redis_conn = get_redis_connection("default")
            redis_conn.hdel("online_users", self.username)
            redis_conn.srem("available_for_random_call", self.username)

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"[DISCONNECT] User disconnected: {self.username} (Channel: {self.channel_name}) Code: {close_code}")
        else:
            logger.info(f"[DISCONNECT] Unauthenticated or uninitialized user disconnected. Code: {close_code}")


    async def receive(self, text_data):
        if not self.user or not self.user.is_authenticated:
            logger.warning(f"[RECEIVE] Message from unauthenticated channel. Ignored.")
            return

        logger.debug(f"[RECEIVE] From {self.username}: {text_data[:200]}...") # لاگ کردن بخشی از پیام برای جلوگیری از لاگ‌های طولانی
        try:
            data = json.loads(text_data)
            msg_type = data.get("type")
            target_username = data.get("target") # برای offer, answer, ice

            redis_conn = get_redis_connection("default")

            if msg_type == "get_random_user":
                # کاربر فعلی را از لیست کاربران قابل انتخاب برای تماس رندوم حذف موقت می‌کنیم
                # redis_conn.srem("available_for_random_call", self.username)
                random_target = await self._get_random_user(self.username)
                logger.info(f"[RANDOM_USER_REQUEST] {self.username} requested random user. Found: {random_target}")
                if random_target:
                    # # کاربر انتخاب شده را هم از لیست حذف می‌کنیم تا درگیر تماس دیگری نشود
                    # redis_conn.srem("available_for_random_call", random_target)
                    # TODO: یک مکانیزم بهتر برای "مشغول بودن" کاربران پیاده‌سازی شود.
                    # مثلاً وضعیت کاربر را در Redis تغییر دهید (idle, busy)
                    pass

                await self.send(text_data=json.dumps({
                    "type": "random_user",
                    "target": random_target # می‌تواند None باشد
                }))

            elif target_username:
                target_channel_name = redis_conn.hget("online_users", target_username)
                if target_channel_name:
                    target_channel_name = target_channel_name.decode()
                    message_to_send = data.copy() # ایجاد کپی برای جلوگیری از تغییرات ناخواسته
                    message_to_send["sender"] = self.username # مهم: فرستنده را اضافه می‌کنیم

                    logger.info(f"[FORWARD] {self.username} -> {target_username} (Channel: {target_channel_name}): Type: {msg_type}")
                    await self.channel_layer.send(
                        target_channel_name,
                        {
                            "type": "send.sdp", # این تابع در consumer هدف اجرا می‌شود
                            "data": message_to_send
                        }
                    )
                else:
                    logger.warning(f"[ERROR] Target user '{target_username}' not online or channel not found.")
                    # می‌توانید به فرستنده پیام دهید که کاربر آفلاین است
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": f"User {target_username} is not online."
                    }))
            else:
                logger.warning(f"[INVALID_MESSAGE] No target specified for message type {msg_type} from {self.username}")

        except json.JSONDecodeError:
            logger.error(f"[ERROR] Invalid JSON received from {self.username}: {text_data}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to process message from {self.username}: {e}", exc_info=True)

    # این تابع برای ارسال پیام‌هایی است که از طریق channel_layer دریافت می‌شوند
    async def send_sdp(self, event):
        data = event["data"]
        logger.debug(f"[SEND_SDP] To {self.username} (via channel_layer): {str(data)[:200]}...")
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async # چون به Redis دسترسی داریم، این دکوراتور لازم نیست مگر اینکه به دیتابیس جنگو هم نیاز باشد
    def _get_random_user(self, exclude_username):
        redis_conn = get_redis_connection("default")
        # کاربران آنلاین که خود کاربر فعلی نیستند
        candidates = [u.decode() for u in redis_conn.smembers("available_for_random_call") if u.decode() != exclude_username]
        
        if not candidates:
            logger.info(f"No random user found for {exclude_username}. Candidates were empty or only self.")
            return None
        
        selected_user = random.choice(candidates)
        logger.info(f"Random user selected for {exclude_username}: {selected_user} from {candidates}")
        return selected_user