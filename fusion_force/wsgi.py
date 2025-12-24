# fusion_force/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusion_force.settings')

application = get_wsgi_application()

# FIXED: Use correct path for WhiteNoise
from whitenoise import WhiteNoise
from pathlib import Path

# Get the BASE_DIR from settings
BASE_DIR = Path(__file__).resolve().parent.parent
static_root = BASE_DIR / 'staticfiles'

# Only use WhiteNoise if staticfiles directory exists
if static_root.exists():
    application = WhiteNoise(application, root=str(static_root))
else:
    print(f"⚠️ Warning: staticfiles directory not found at {static_root}")