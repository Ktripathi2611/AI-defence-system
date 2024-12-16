"""
WSGI config for ai_defense project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_defense.settings')

application = get_wsgi_application()
