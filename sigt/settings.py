import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dz#i6co##%v(kn4ai=#$ik_!3+fudyoip)&jw(d3_(wgm@j^1c'

DEBUG = True

ALLOWED_HOSTS = os.environ.get(
    'SIGT_ALLOWED_HOSTS',
    '127.0.0.1,localhost,172.16.5.76',
).split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',
    'inventario',
    'mesa_ayuda',
    'mantenimiento',
    'reportes',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'sigt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sigt.context_processors.sidebar_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sigt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (producción). Para activarlo, define las variables de entorno y
# cambia el ENGINE por 'django.db.backends.postgresql'.
# Ejemplo:
#   DATABASES = {
#       'default': {
#           'ENGINE': 'django.db.backends.postgresql',
#           'NAME': os.environ.get('SIGT_DB_NAME', 'sigt'),
#           'USER': os.environ.get('SIGT_DB_USER', 'postgres'),
#           'PASSWORD': os.environ.get('SIGT_DB_PASSWORD', ''),
#           'HOST': os.environ.get('SIGT_DB_HOST', 'localhost'),
#           'PORT': os.environ.get('SIGT_DB_PORT', '5432'),
#       }
#   }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Caracas'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'usuarios.User'
