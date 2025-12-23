# settings.py - COMPLETE FIXED VERSION
import os
import sys
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# ========== ERROR TRAPPING ==========
try:
    print("🚀 Loading Django settings...")
    
    load_dotenv()
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"✅ BASE_DIR: {BASE_DIR}")
    
    # ========== SECURITY ==========
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-railway-12345')
    print(f"✅ SECRET_KEY loaded: {'SECRET_KEY' in os.environ}")
    
    # ========== DATABASE CONFIGURATION ==========
    DATABASE_URL = os.environ.get('DATABASE_URL')
    print(f"✅ DATABASE_URL exists: {bool(DATABASE_URL)}")
    
    if DATABASE_URL:
        print("🔵 Using PostgreSQL (Railway/Production)")
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True
            )
        }
        
        if 'sslmode' not in DATABASES['default'].get('OPTIONS', {}):
            DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'require'
    else:
        print("🟢 Using SQLite (Local Development)")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    
    # ========== DEBUG & HOSTS ==========
    IS_RAILWAY = bool(DATABASE_URL) and 'railway' in DATABASE_URL.lower()
    
    # Better DEBUG handling
    if IS_RAILWAY:
        DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    else:
        # Default to True for local development
        DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # ALLOWED_HOSTS - FIXED (no port numbers, proper commas)
    ALLOWED_HOSTS = []
    
    if DEBUG:
        # Local development hosts
        ALLOWED_HOSTS.extend([
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '[::1]',  # IPv6 localhost
        ])
        
        # Add local network IP for testing on other devices
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            ALLOWED_HOSTS.append(local_ip)
            print(f"✅ Local IP detected: {local_ip}")
        except Exception:
            pass
    else:
        # Production hosts
        ALLOWED_HOSTS.extend([
            "fusionforcellc-production.up.railway.app",
            ".railway.app",  # All railway subdomains
            "www.pamela-fusionforce.com",
            "pamela-fusionforce.com",
        ])
    
    print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    
    # CSRF_TRUSTED_ORIGINS - FIXED (proper URLs, proper commas)
    CSRF_TRUSTED_ORIGINS = [
        'https://*.up.railway.app',
        'https://*.railway.app',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://www.pamela-fusionforce.com',
        'https://pamela-fusionforce.com',
    ]
    
    # Add local network origin if available
    if DEBUG:
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            CSRF_TRUSTED_ORIGINS.append(f'http://{local_ip}:8000')
            CSRF_TRUSTED_ORIGINS.append(f'http://{local_ip}:3000')
        except Exception:
            pass
    
    # ========== SECURITY SETTINGS ==========
    if not DEBUG and IS_RAILWAY:
        # Production security
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_BROWSER_XSS_FILTER = True
        SECURE_CONTENT_TYPE_NOSNIFF = True
        SECURE_HSTS_SECONDS = 31536000  # 1 year
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        print("🔒 Production security enabled")
    else:
        # Development security (relaxed)
        SECURE_SSL_REDIRECT = False
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
        SECURE_HSTS_SECONDS = 0
        print("🔓 Development security")
    
    # ========== APPLICATION DEFINITION ==========
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'whitenoise.runserver_nostatic',
        'main.apps.MainConfig',  # Your custom app
    ]
    
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    ROOT_URLCONF = 'fusion_force.urls'
    
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    
    WSGI_APPLICATION = 'fusion_force.wsgi.application'
    
    # ========== PASSWORD VALIDATION ==========
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]
    
    # ========== INTERNATIONALIZATION ==========
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_TZ = True
    
    # ========== STATIC FILES ==========
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    os.makedirs(STATIC_ROOT, exist_ok=True)
    
    static_dir = BASE_DIR / 'static'
    if static_dir.exists():
        STATICFILES_DIRS = [static_dir]
        print(f"✅ Found static directory: {static_dir}")
    else:
        STATICFILES_DIRS = []
        print("ℹ️ No static directory found")
    
    # ========== MEDIA FILES ==========
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    print(f"✅ Media directory: {MEDIA_ROOT}")
    
    # ========== WHITENOISE CONFIG ==========
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_AUTOREFRESH = DEBUG
    WHITENOISE_USE_FINDERS = DEBUG
    WHITENOISE_MANIFEST_STRICT = False
    
    # ========== DEFAULT PRIMARY KEY ==========
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
    
    # ========== SESSION SETTINGS ==========
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
    SESSION_SAVE_EVERY_REQUEST = True
    
    # ========== CUSTOM ADMIN SETTINGS ==========
    ADMIN_SITE_HEADER = "FUSION-FORCE ADMIN"
    ADMIN_SITE_TITLE = "Fusion Force Administration"
    ADMIN_SITE_INDEX_TITLE = "Welcome to Fusion Force Administration"
    
    # ========== LOGGING ==========
    if DEBUG:
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
            'loggers': {
                'django': {
                    'handlers': ['console'],
                    'level': 'INFO',
                    'propagate': False,
                },
            },
        }
    
    print("✅ All settings loaded successfully!")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR in settings.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)