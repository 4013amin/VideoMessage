from pathlib import Path
import os

# مسیر اصلی پروژه
BASE_DIR = Path(__file__).resolve().parent.parent

# کلید مخفی (در تولید از متغیر محیطی استفاده کنید)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-rj7opk%p)4p6du4g8mqqm7_t28@0ht4isgbd7yer$%hw(*_!pf')

# حالت دیباگ (برای تولید False باشد)
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# اجازه دادن به همه هاست‌ها (برای تولید می‌توانید دامنه خاص را تنظیم کنید)
ALLOWED_HOSTS = ['*']

# اپلیکیشن‌های نصب‌شده
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'websocket',  # اپلیکیشن WebSocket
    'channels',  # برای پشتیبانی از WebSocket
]

# تنظیمات Redis برای Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://:HZZAo6Lqgna6Vm07240VN7u1@videochat:6379/0")],
        },
    },
}

# میان‌افزارها
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# تنظیمات URL
ROOT_URLCONF = 'VideoChat.urls'

# تنظیمات قالب‌ها
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# تنظیمات WSGI و ASGI
WSGI_APPLICATION = 'VideoChat.wsgi.application'
ASGI_APPLICATION = 'VideoChat.asgi.application'

# تنظیمات دیتابیس (SQLite برای سادگی)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# اعتبارسنجی رمز عبور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# تنظیمات زبان و زمان
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# تنظیمات فایل‌های استاتیک
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# تنظیمات فایل‌های رسانه
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# نوع فیلد خودکار
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# تنظیمات امنیتی
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')