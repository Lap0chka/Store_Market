from .base import *
import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lessthanten',
        'USER': 'store_username',
        'PASSWORD': 'store_password',
    }
}



STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

LOGIN_REDIRECT_URL = 'user:profile'

#export DJANGO_SETTINGS_MODULE=myshop.settings.local
