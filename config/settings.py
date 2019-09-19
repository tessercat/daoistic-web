""" Daoistic project settings module. """
import ast
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load SETTINGS from a dict literal.
with open(os.path.join(BASE_DIR, 'var', 'settings.py')) as settings_file:
    SETTINGS = ast.literal_eval(settings_file.read())


# Required custom settings

SECRET_KEY = SETTINGS['SECRET_KEY']


# Other custom settings

ADMINS = SETTINGS.get('ADMINS') or (('Host admin', 'root@localhost'),)

ALLOWED_HOSTS = SETTINGS.get('ALLOWED_HOSTS') or []

DEBUG = SETTINGS.get('DEBUG') or False

EMAIL_SUBJECT_PREFIX = '[Daoistic] '

FIREWALL_API_PORT = SETTINGS.get('FIREWALL_API_PORT') or 8200

SERVER_EMAIL = SETTINGS.get('SERVER_EMAIL') or 'root@localhost'

TIME_ZONE = SETTINGS.get('TIME_ZONE') or 'UTC'


# Header and cookie definition

# Assume no port in nginx HTTP-X-FORWARDED-HOST for CSRF match.
# https://stackoverflow.com/questions/27533011

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True

USE_X_FORWARDED_HOST = True

USE_X_FORWARDED_PORT = True


# Application definition

AUTH_USER_MODEL = 'common.User'

INSTALLED_APPS = [
    'common.apps.CommonConfig',
    'unihan.apps.UnihanConfig',
    'daoistic.apps.DaoisticConfig',
    'blog.apps.BlogConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.middleware.FirewallMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'var', 'db.sqlite3'),
    }
}


# Cache
# https://docs.djangoproject.com/en/2.1/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.' + (
            'dummy.DummyCache' if DEBUG else 'memcached.MemcachedCache'
        ),
        'LOCATION': '127.0.0.1:11211',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
