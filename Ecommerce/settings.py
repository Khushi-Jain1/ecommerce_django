"""
Django settings for Ecommerce project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = [ '192.168.43.173', 'www.e-shopper.in', 'www.khushijain.in']
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'core.user.apps.UserConfig',
    'customAdmin.apps.CustomadminConfig',
    'reactCore.apps.ReactcoreConfig',
    'customUser.apps.CustomuserConfig',
    'phonenumber_field',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'paypal.standard.ipn',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'rest_framework',
    'corsheaders',
    'social_django', 
    "django_cron",

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', 
    # 'knox',
]

SITE_ID = 1

AUTH_USER_MODEL = 'customAdmin.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

CRON_CLASSES = [
    'customUser.crons.MailWishlist'
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    # )
}

AUTHENTICATION_BACKENDS = [
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.github.GithubOAuth2',

    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'Ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'static','templates')
            # os.path.join(BASE_DIR, 'customAdmin','templates'),
            # os.path.join(BASE_DIR, 'customUser', 'templates'),
            # os.path.join(BASE_DIR, 'Ecommerce', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends', 
                'social_django.context_processors.login_redirect', 
            ],
        },
    },
]

WSGI_APPLICATION = 'Ecommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('Database_name'),
        'USER': config('Database_user'),
        'PASSWORD': config('Database_password'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/3.2/howto/static-files/
# SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static/')
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('email_host')
EMAIL_HOST_PASSWORD = config('email_host_password')
ACCOUNT_EMAIL_VERIFICATION = 'none'

# LOGIN_URL = '/admin/'
# LOGIN_REDIRECT_URL = '/admin/dashboard/'


# django-paypal settings
PAYPAL_RECEIVER_EMAIL = 'dusty.bun@gmail.com'
PAYPAL_TEST = True

# MAILCHIMP CREDENTIALS
MAILCHIMP_API_KEY = "7a7ab8ee61d7e5384ebdd7d12461d1d0-us5"
MAILCHIMP_DATA_CENTER = "us5"
MAILCHIMP_EMAIL_LIST_ID = "fc18f6006b"


SOCIAL_AUTH_FACEBOOK_KEY = '290746595987865'       # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = '98699872ed75413dc332d7f3d7b35557'  # App Secret

SOCIAL_AUTH_GITHUB_KEY = 'fe01de7f4d0850361eb5'
SOCIAL_AUTH_GITHUB_SECRET = '5fc6db3b1fcba1d8a3d27cfbc2fc2178100bb3ad'

# SESSION_COOKIE_SECURE=False


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# SECURE_SSL_REDIRECT = False


