"""
Django settings for NonogramServer project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import environ
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR.parent))


env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("NONOGRAM_SERVER_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = [
    "localhost",
    env("NONOGRAM_SERVER_HOST"),
    env("API_SERVER_HOST"),
    env("DB_HOST"),
]

API_SERVER_PROTOCOL = env("API_SERVER_PROTOCOL")
API_SERVER_HOST = env("API_SERVER_HOST")
API_SERVER_PORT = env("API_SERVER_PORT")
ENABLE_PROMETHEUS = env.bool("ENABLE_PROMETHEUS")
if ENABLE_PROMETHEUS:
    PROMETHEUS_PROTOCOL = env("PROMETHEUS_PROTOCOL")
    PROMETHEUS_HOST = env("PROMETHEUS_HOST")
    PROMETHEUS_PORT = env("PROMETHEUS_PORT")

CORS_ALLOWED_ORIGINS = [
    f"{API_SERVER_PROTOCOL}://{API_SERVER_HOST}:{API_SERVER_PORT}",
    f"{API_SERVER_PROTOCOL}://localhost:{API_SERVER_PORT}",
]


if ENABLE_PROMETHEUS:
    CORS_ALLOWED_ORIGINS += [
        f"{PROMETHEUS_PROTOCOL}://{PROMETHEUS_HOST}:{PROMETHEUS_PORT}",
        f"{PROMETHEUS_PROTOCOL}://localhost:{PROMETHEUS_PORT}",
    ]

# Application definition

INSTALLED_APPS = [
    'NonogramServer.apps.NonogramserverConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'NonogramServer.urls'

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

WSGI_APPLICATION = 'NonogramServer.wsgi.application'
ASGI_APPLICATION = 'NonogramServer.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        # "OPTIONS": {
        #     # "service": "nonogram_service",
        #     "passfile": ".nonogram_pgpass",
        # },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

CACHE_HOST = env("CACHE_HOST")
CACHE_PORT = env("CACHE_PORT")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"http://{CACHE_HOST}:{CACHE_PORT}",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
