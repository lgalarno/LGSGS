"""
Django settings for LGSGS project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import dotenv_values

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
config = dotenv_values(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(config["DEBUG"]) == "1"  # 1 == True

ALLOWED_HOSTS = config["ALLOWED_HOSTS"].split(',') if config["ALLOWED_HOSTS"] else []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "crispy_forms",
    "crispy_bootstrap5",
    'django_celery_beat',
    # custom app
    "accounts.apps.AccountsConfig",
    "assets.apps.AssetsConfig"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "LGSGS.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "LGSGS.wsgi.application"


######################################################################
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
######################################################################
DATABASES = {
    'default': {
        'ENGINE': config.get('DATABASE_ENGINE'),
        'HOST': config.get('DATABASE_HOST'),
        'PORT': config.get('DATABASE_PORT'),
        'USER': config.get('DATABASE_USER'),
        'PASSWORD': config.get('DATABASE_PASSWORD'),
        'NAME': config.get('DATABASE_NAME'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True, },
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FROM_EMAIL = config["FROM_EMAIL"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]

######################################################################
# CUSTOM USER
######################################################################
AUTH_USER_MODEL = "accounts.User"

######################################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
######################################################################
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = config.get('STATIC_ROOT')
MEDIA_ROOT = config.get('MEDIA_ROOT', BASE_DIR / '..' / "media")

######################################################################
# LOGIN/LOGOUT REDIRECT
######################################################################
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/'

######################################################################
# CRISPY_FORMS
######################################################################
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

######################################################################
# CELERY
######################################################################
CELERY_BROKER_URL = config["REDIS_URL"]
CELERY_RESULT_BACKEND = config["REDIS_URL"]
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
UPDT_INTERVAL = int(config["UPDT_INTERVAL"])

######################################################################
# CACHES
######################################################################
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config["REDIS_URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}