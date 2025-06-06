import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

# نامی برای کلید Redis که لیست کاربران آنلاین را نگه می‌دارد
ONLINE_USERS_REDIS_KEY = "online_users_for_call"

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # اگر کاربر لاگین نکرده باشد، اتصال را رد می‌کنیم
        if not self.user.is_authenticated:
            await self.close()
            return

        self.username = self.user.username
        self.room_group_name = f"user_{self.username}"

        # اتصال به گروه شخصی کاربر (برای دریافت پیام‌های مستقیم)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # افزودن کاربر به لیست کاربران آنلاین در Redis
        # از یک Set در Redis استفاده می‌کنیم تا کاربران تکراری نداشته باشیم
        cache.sadd(ONLINE_USERS_REDIS_KEY, self.username)

        await self.accept()
        print(f"User {self.username} connected and added to online set.")

    async def disconnect(self, close_code):
        if not self.user.is_authenticated:
            return

        # حذف کاربر از لیست کاربران آنلاین در Redis
        cache.srem(ONLINE_USERS_REDIS_KEY, self.username)
        print(f"User {self.username} disconnected and removed from online set.")

        # خروج از گروه شخصی
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        target_username = data.get('target')

        print(f"Received message type '{message_type}' from {self.username}")

        if message_type == 'get_random_user':
            # گرفتن تمام کاربران آنلاین از Redis
            online_users = cache.smembers(ONLINE_USERS_REDIS_KEY)
            # تبدیل به لیست و حذف کاربر فعلی از لیست کاندیدها
            available_users = [user.decode('utf-8') for user in online_users if user.decode('utf-8') != self.username]

            if available_users:
                random_user = random.choice(available_users)
                print(f"Found random user '{random_user}' for {self.username}")
                await self.send(text_data=json.dumps({
                    'type': 'random_user',
                    'target': random_user
                }))
            else:
                print(f"No available users for {self.username}")
                await self.send(text_data=json.dumps({
                    'type': 'random_user',
                    'target': None # یا یک پیام خطا
                }))
            return

        # برای پیام‌های دیگر، آن‌ها را به کاربر هدف ارسال می‌کنیم
        if target_username:
            # اضافه کردن فرستنده به پیام
            data['sender'] = self.username
            
            # ارسال پیام به گروه کاربر هدف
            await self.channel_layer.group_send(
                f"user_{target_username}",
                {
                    'type': 'forward_message', # نام هندلر در این کلاس
                    'message': data
                }
            )

    # این متد پیام را از group_send دریافت کرده و به کلاینت ارسال می‌کند
    async def forward_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))