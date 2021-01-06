""" Daoistic project settings module. """
import ast
import os
import random


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load SETTINGS from a dict literal.
with open(os.path.join(BASE_DIR, 'var', 'settings.py')) as settings_file:
    SETTINGS = ast.literal_eval(settings_file.read())

# Load SECRET_KEY from file or write a new one. Django 2.2.
SECRET_KEY_FILE = os.path.join(BASE_DIR, 'var', 'secret_key')
if os.path.isfile(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE) as secret_fd:
        SECRET_KEY = secret_fd.read().strip()
else:
    SECRET_KEY = ''.join(random.choice(
        'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    ) for _ in range(50))
    with open(SECRET_KEY_FILE, 'w') as secret_fd:
        secret_fd.write(SECRET_KEY)


# Required custom settings

ADMINS = SETTINGS['ADMINS']

ALLOWED_HOSTS = SETTINGS['ALLOWED_HOSTS']

FIREWALL_API_PORT = SETTINGS['FIREWALL_API_PORT']

SERVER_EMAIL = SETTINGS['SERVER_EMAIL']

TIME_ZONE = SETTINGS['TIME_ZONE']


# Other custom settings

CSRF_FAILURE_VIEW = 'common.views.custom403'

DEBUG = False

EMAIL_SUBJECT_PREFIX = '[daoistic] '

# PROTECTED_PATHS = (
#     '/metrics',
# )


# Header and cookie definition

# Assume no port in nginx HTTP-X-FORWARDED-HOST for CSRF match.
# https://stackoverflow.com/questions/27533011

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True

USE_X_FORWARDED_HOST = True

USE_X_FORWARDED_PORT = True


# Application definition

INSTALLED_APPS = [
    # 'django_prometheus',
    'firewall.apps.FirewallConfig',
    'common.apps.CommonConfig',
    'unihan.apps.UnihanConfig',
    'blog.apps.BlogConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    # 'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'common.middleware.ProtectedPathsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'firewall.middleware.FirewallMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_prometheus.middleware.PrometheusAfterMiddleware',
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

WSGI_APPLICATION = 'project.wsgi.application'


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
