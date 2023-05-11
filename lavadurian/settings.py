"""
Django settings for lavadurian project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from google.oauth2 import service_account
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q$*53q$q$44eulno7irpwcb#2t6)5a+w9gz9irta7ir_@g9r#1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '188.166.177.139',
                 'www.lavadurian.com', 'lavadurian.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',

    'ckeditor',
    'bootstrap4',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'cloudinary',

    'myapp',
    'Pages',
    'Members',
    'News',
    'Store',
    'Cart',
    'DurianAPI',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1

LOGIN_REDIRECT_URL = "/"

# Enable in production host
# social login
os.environ['HTTPS'] = "on"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQURIED = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lavadurian.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'lavadurian.wsgi.application'

# REST Framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ssk_durain',
        'USER': 'django',
        'PASSWORD': 'b0bd21ab07c41ea76e8fec3e9e11c65b',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bangkok'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ---------------------------------------------
# * Setup Project Storage
# * Using Google Cloud Storage
# * https://www.youtube.com/watch?v=hJmkECmXyxY&t=306s
# * for media in bucket

#! get credentials
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    "credentials.json")

# ! google cloud storeage detail
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_PROJECT_ID = 'lava-durian'
GS_BUCKET_NAME = 'lavadurian'
MEDIA_ROOT = "media/"
UPLOAD_ROOT = 'media/uploads/'
MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)

# ---------------------------------------------

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Social Login

# a personal preference. True by default. I don't want users to be interrupted by logging in
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
# a personal preference. I don't want to add 'i don't remember my username' like they did at Nintendo, it's stupidwill be used for login
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True  # False by default
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True  # True by default
# ACCOUNT_LOGOUT_REDIRECT_URL = '/login'
ACCOUNT_USERNAME_BLACKLIST = ['suka', 'blyat', ]  # :D
ACCOUNT_USERNAME_MIN_LENGTH = 4  # a personal preference
# None by default (to ask 'Remember me?'). I want the user to be always logged in
ACCOUNT_SESSION_REMEMBER = True

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'chamber.sisaket@gmail.com'
EMAIL_HOST_PASSWORD = 'fwrfrrmjemvcsnsv'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
