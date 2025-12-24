# fusion_force/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusion_force.settings')

application = get_wsgi_application()

# Add this for WhiteNoise to serve static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))