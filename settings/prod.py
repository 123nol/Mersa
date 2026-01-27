# settings/prod.py
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]

SECRET_KEY = os.getenv("SECRET_KEY")  # must be set in server env

# Security
SECURE_SSL_REDIRECT = True
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
    'handlers': {'file': {
        'level': 'WARNING',
        'class': 'logging.FileHandler',
        'filename': '/var/log/django/django.log',
    }},
    'loggers': {'django': {'handlers': ['file'], 'level': 'WARNING', 'propagate': True}},
}
