import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']


# اپلیکیشن‌ها
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # اپلیکیشن‌های مربوط به auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # WebSocket support
    'channels',

    # اپلیکیشن خودت
    'websocket',
    
]

# Middlewareها
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'VideoChat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # اختیاری برای قالب سفارشی
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # الزامی برای allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'VideoChat.wsgi.application'
ASGI_APPLICATION = 'VideoChat.asgi.application'

# پایگاه داده
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Channel Layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Redis cache (اختیاری)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# اعتبارسنجی پسورد
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# تنظیمات allauth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)



SITE_ID = 1

# تنظیمات ورود
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# تنظیمات Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '70809775459-7fmtq0c03kgs9jm145dvak6ca1iundaq.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}


# Google OAuth credentials
SOCIALACCOUNT_PROVIDERS['google']['APP'] = {
    'client_id': '70809775459-7fmtq0c03kgs9jm145dvak6ca1iundaq.apps.googleusercontent.com',
    'secret': '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',
    'key': ''
}

# زبان و زمان
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# فایل‌های استاتیک
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# مدل کاربر سفارشی
AUTH_USER_MODEL = 'websocket.CustomUser'

# تنظیمات پیش‌فرض
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
