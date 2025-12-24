# settings.py - FIXED VERSION
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
    # Check if we're on Railway (better detection)
    IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ or bool(DATABASE_URL and 'railway' in DATABASE_URL.lower())
    
    # DEBUG handling
    if IS_RAILWAY:
        DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    else:
        DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"✅ DEBUG mode: {DEBUG}")
    print(f"✅ IS_RAILWAY: {IS_RAILWAY}")
    
    # ALLOWED_HOSTS
    ALLOWED_HOSTS = []
    
    if DEBUG:
        ALLOWED_HOSTS.extend([
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '[::1]',
        ])
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
        ALLOWED_HOSTS.extend([
            "fusionforcellc-production.up.railway.app",
            ".railway.app",
            "www.pamela-fusionforce.com",
            "pamela-fusionforce.com",
        ])
    
    print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    
    # CSRF_TRUSTED_ORIGINS
    CSRF_TRUSTED_ORIGINS = [
        'https://*.up.railway.app',
        'https://*.railway.app',
        'https://www.pamela-fusionforce.com',
        'https://pamela-fusionforce.com',
    ]
    
    if DEBUG:
        CSRF_TRUSTED_ORIGINS.extend([
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'http://localhost:3000',
            'http://127.0.0.1:3000',
        ])
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
    if not DEBUG:
        # Production security
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
        # Development security
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
        'cloudinary',
        'cloudinary_storage',
        'main.apps.MainConfig',
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
    
    # ========== MEDIA FILES CONFIGURATION - FIXED ==========
    # Check Cloudinary credentials
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    HAS_CLOUDINARY_CREDENTIALS = all([
        CLOUDINARY_CLOUD_NAME,
        CLOUDINARY_API_KEY,
        CLOUDINARY_API_SECRET
    ])
    
    print(f"🌥️ Cloudinary credentials available: {HAS_CLOUDINARY_CREDENTIALS}")
    
    if HAS_CLOUDINARY_CREDENTIALS:
        # USE CLOUDINARY IF CREDENTIALS EXIST (regardless of Railway/local)
        print("✅ Configuring Cloudinary for media storage")
        
        # Import and configure Cloudinary
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        
        # Cloudinary storage settings
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
            'API_KEY': CLOUDINARY_API_KEY,
            'API_SECRET': CLOUDINARY_API_SECRET,
            'SECURE': True,
        }
        
        # Use Cloudinary for media files
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        
        # Set media URL to Cloudinary
        MEDIA_URL = f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/'
        
        # No local media root needed when using Cloudinary
        MEDIA_ROOT = ''
        
        print(f"✅ Media files will be stored in Cloudinary: {CLOUDINARY_CLOUD_NAME}")
        
    elif IS_RAILWAY and not HAS_CLOUDINARY_CREDENTIALS:
        # ON RAILWAY WITHOUT CLOUDINARY - USE RAILWAY VOLUME
        print("⚠️  On Railway without Cloudinary - using Railway volume for media")
        
        # Use Railway volume path for media
        MEDIA_ROOT = '/data/media'
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        MEDIA_URL = '/media/'
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
        
        print(f"✅ Using Railway volume for media: {MEDIA_ROOT}")
        
    else:
        # LOCAL DEVELOPMENT WITHOUT CLOUDINARY
        print("💾 Using local media storage (development)")
        MEDIA_URL = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
        print(f"✅ Local media directory: {MEDIA_ROOT}")
    
    # ========== WHITENOISE CONFIG ==========
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_AUTOREFRESH = DEBUG
    WHITENOISE_USE_FINDERS = DEBUG
    WHITENOISE_MANIFEST_STRICT = False
    
    # ========== DEFAULT PRIMARY KEY ==========
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
    
    # ========== SESSION SETTINGS ==========
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 1209600
    SESSION_SAVE_EVERY_REQUEST = True
    
    # ========== CUSTOM ADMIN SETTINGS ==========
    ADMIN_SITE_HEADER = "FUSION-FORCE ADMIN"
    ADMIN_SITE_TITLE = "Fusion Force Administration"
    ADMIN_SITE_INDEX_TITLE = "Welcome to Fusion Force Administration"
    
    # ========== LOGGING ==========
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
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
            'main': {
                'handlers': ['console'],
                'level': 'DEBUG' if DEBUG else 'INFO',
                'propagate': False,
            },
        },
    }
    
    # ========== FINAL CONFIG CHECK ==========
    print(f"📁 STATIC_ROOT: {STATIC_ROOT}")
    print(f"📁 MEDIA_ROOT: {MEDIA_ROOT}")
    print(f"🔗 MEDIA_URL: {MEDIA_URL}")
    print(f"💾 DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")
    print(f"📦 STATICFILES_STORAGE: {STATICFILES_STORAGE}")
    
    print("✅ All settings loaded successfully!")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR in settings.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)