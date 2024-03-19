from .base import *
import os

DEBUG = False

ADMINS = [
    ('admin', ''),
]

ALLOWED_HOSTS = ['less-than-ten.com', 'www.less-than-ten.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lessthanten',
        'USER': 'store_username',
        'PASSWORD': 'store_password',
        'HOST': 'db',
        'PORT': 5432, }
}


REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]

STATIC_ROOT = BASE_DIR / 'static'


# Безопасность
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True