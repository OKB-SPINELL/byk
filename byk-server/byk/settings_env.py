# -*- coding: utf-8 -*-
import typing as ty  # noqa: F401

import os
from .settings import *  # noqa: F403,F401

DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() in {'true', '1', 'yes'}

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if os.getenv('DJANGO_ALLOWED_HOSTS') else [
    '*',
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: PLEASE MAKE SURE TO SET A DIFFERENT POSTGRESQL_PASSWORD FOR PRODUCTION USE!
#                   DO NOT USE THE DEFAULT PASSWORD IN PRODUCTION ENVIRONMENTS!
POSTGRESQL_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRESQL_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRESQL_NAME = os.getenv('POSTGRES_DB', 'byk-server')
POSTGRESQL_USER = os.getenv('POSTGRES_USER', 'byk_user')
POSTGRESQL_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'byk_password')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': POSTGRESQL_HOST,
        'PORT': POSTGRESQL_PORT,
        'NAME': POSTGRESQL_NAME,
        'USER': POSTGRESQL_USER,
        'PASSWORD': POSTGRESQL_PASSWORD,
    }
}

# Auth0
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID', '')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET', '')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', '')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
