from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ["mersa.onrender.com"]

# Secret key must come from environment
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True

CSRF_TRUSTED_ORIGINS = ["https://mersa.onrender.com"]

# Logging for Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}

# DATABASE: use DATABASE_URL from Render
db_from_env = dj_database_url.config(conn_max_age=600)
if db_from_env:
    DATABASES["default"].update(db_from_env)
else:
    raise Exception("DATABASE_URL environment variable not set")
