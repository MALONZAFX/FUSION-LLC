"""
WSGI config for fusion_force project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusion_force.settings')

application = get_wsgi_application()