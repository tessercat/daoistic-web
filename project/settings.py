""" Daoistic project settings module. """
import ast
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key


BASE_DIR = Path(__file__).resolve().parent.parent


# Load SECRET_KEY from file or write a new one.
SECRET_KEY_FILE = BASE_DIR / 'var' / 'secret_key'
if os.path.isfile(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, encoding='utf-8') as secfd:
        SECRET_KEY = secfd.read().strip()
else:
    SECRET_KEY = get_random_secret_key()
    with open(SECRET_KEY_FILE, 'w', encoding='utf-8') as secfd:
        secfd.write(SECRET_KEY)


# Load ENV from Python dict literal.
with open(BASE_DIR / 'var' / 'settings.py', encoding='utf-8') as setfd:
    ENV = ast.literal_eval(setfd.read())

ADMINS = ENV['ADMINS']

ALLOWED_HOSTS = (
    ENV['ALLOWED_HOST'],
    'localhost'
)

FIREWALL_API_PORT = ENV['FIREWALL_API_PORT']

SERVER_EMAIL = ENV['SERVER_EMAIL']

TIME_ZONE = ENV['TIME_ZONE']


# Other custom settings

CSRF_FAILURE_VIEW = 'common.views.custom403'

DEBUG = False

EMAIL_SUBJECT_PREFIX = '[daoistic] '

# https://docs.djangoproject.com/en/4.0/topics/security/#ssl-https
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# nginx separate X-Forwarded-Host and X-Forwarded-Port for CSRF match
# https://stackoverflow.com/questions/27533011
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# nginx X-Forwarded-Proto is $scheme for is_secure CSRF match
# https://stackoverflow.com/questions/11441832
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'common.apps.CommonConfig',
    'unihan.apps.UnihanConfig',
    'entry.apps.EntryConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.middleware.AdminKnockMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'var' / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.' + (
            'dummy.DummyCache' if DEBUG else 'memcached.PyMemcacheCache'
        ),
        'LOCATION': '127.0.0.1:11211',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'
