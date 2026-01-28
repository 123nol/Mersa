# settings/prod.py
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com", "mersa.onrender.com"] 

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")  # must be set in server env

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

CSRF_TRUSTED_ORIGINS = [
    "https://mersa.onrender.com",
]
