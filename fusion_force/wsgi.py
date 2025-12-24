# fusion_force/wsgi.py - SIMPLE VERSION
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusion_force.settings')

application = get_wsgi_application()

# REMOVE WhiteNoise completely - Django will handle static files