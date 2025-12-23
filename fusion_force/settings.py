# settings.py - COMPLETE FIXED VERSION FOR RAILWAY
import os
import sys
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# ========== ERROR TRAPPING ==========
# This catches crashes and shows errors in logs
try:
    print("🚀 Loading Django settings...")
    
    # Load environment variables
    load_dotenv()
    
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"✅ BASE_DIR: {BASE_DIR}")
    
    # ========== SECURITY ==========
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-railway-12345')
    print(f"✅ SECRET_KEY loaded: {'SECRET_KEY' in os.environ}")
    
    # ========== DATABASE CONFIGURATION ==========
    DATABASE_URL = os.environ.get('DATABASE_URL')
    print(f"✅ DATABASE_URL exists: {bool(DATABASE_URL)}")
    
    # FIXED: Use simpler database config
    if DATABASE_URL:
        # PRODUCTION: PostgreSQL on Railway
        print("🔵 Using PostgreSQL (Railway/Production)")
        
        # FIXED: Removed ssl_require=True which causes Railway connection issues
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True
                # REMOVED: ssl_require=True - Railway handles SSL automatically
            )
        }
        
        # Add SSL options if needed
        if 'sslmode' not in DATABASES['default'].get('OPTIONS', {}):
            DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'require'
    else:
        # DEVELOPMENT: SQLite locally
        print("🟢 Using SQLite (Local Development)")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    
    # ========== DEBUG & HOSTS ==========
    # Check environment - SIMPLIFIED
    IS_RAILWAY = 'DATABASE_URL' in os.environ and 'railway' in os.environ.get('DATABASE_URL', '').lower()
    
    # Debug mode - allow override
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Hosts - ALWAYS allow all for Railway
    ALLOWED_HOSTS = ['*']
    
    # CSRF settings for Railway domains
    CSRF_TRUSTED_ORIGINS = [
        'https://*.up.railway.app',
        'https://*.railway.app',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    ]
    
    # Security settings - only if NOT debug
    if not DEBUG and IS_RAILWAY:
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_BROWSER_XSS_FILTER = True
        SECURE_CONTENT_TYPE_NOSNIFF = True
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        print("🔒 Production security enabled")
    else:
        SECURE_SSL_REDIRECT = False
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
        SECURE_HSTS_SECONDS = 0
        print("🔓 Development security (no HTTPS)")
    
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    
    # ========== APPLICATION DEFINITION ==========
    INSTALLED_APPS = [
        'main.apps.MainConfig',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'whitenoise.runserver_nostatic',
    ]
    
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
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
    
    # Create staticfiles directory if it doesn't exist
    os.makedirs(STATIC_ROOT, exist_ok=True)
    
    # Only add STATICFILES_DIRS if the directory exists
    static_dir = BASE_DIR / 'static'
    if static_dir.exists():
        STATICFILES_DIRS = [static_dir]
        print(f"✅ Found static directory: {static_dir}")
    else:
        STATICFILES_DIRS = []
        print("ℹ️ No static directory found")
    
    # ========== MEDIA FILES - FIXED FOR RAILWAY ==========
    if IS_RAILWAY:
        # On Railway: Use external storage or disable uploads
        print("⚠️ Railway detected: Media uploads will be TEMPORARY (filesystem is ephemeral)")
        MEDIA_URL = '/media/'  # MUST be '/media/' not 'media/'
        MEDIA_ROOT = BASE_DIR / 'media'
    else:
        # Local development
        MEDIA_URL = 'media/'
        MEDIA_ROOT = BASE_DIR / 'media'
    
    # Create media directory if it doesn't exist
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    print(f"✅ Media directory: {MEDIA_ROOT}")
    
    # WhiteNoise configuration - FIXED
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    WHITENOISE_AUTOREFRESH = DEBUG  # Auto-refresh in debug mode
    
    # IMPORTANT: Add WhiteNoise configuration for media files
    WHITENOISE_ROOT = STATIC_ROOT
    # This allows WhiteNoise to serve media files too
    WHITENOISE_ALLOW_ALL_ORIGINS = True
    
    # ========== DEFAULT PRIMARY KEY ==========
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
    
    # ========== CUSTOM ADMIN SETTINGS ==========
    ADMIN_SITE_HEADER = "FUSION-FORCE ADMIN"
    ADMIN_SITE_TITLE = "Fusion Force Administration"
    
    print("✅ All settings loaded successfully!")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR in settings.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)  # Force crash with error message