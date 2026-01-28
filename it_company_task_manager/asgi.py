"""
ASGI config for it_company_task_manager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os


from django.core.asgi import get_asgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "it_company_task_manager.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()
application = WhiteNoise(django_asgi_app, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))

# Optional: enable gzip compression for faster delivery
application.add_files(os.path.join(os.path.dirname(__file__), 'staticfiles'), prefix='static/')