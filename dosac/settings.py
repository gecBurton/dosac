import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


if APP_HOST := os.environ.get("APP_HOST"):
    ALLOWED_HOSTS = ["localhost", APP_HOST]
    CSRF_TRUSTED_ORIGINS = [f"https://{APP_HOST}"]
    WEBSOCKET_SCHEME = "wss"
    HTTP_SCHEME = "https"

    EMAIL_HOST = os.environ["MAILGUN_SMTP_SERVER"]
    EMAIL_PORT = os.environ["MAILGUN_SMTP_PORT"]
    EMAIL_HOST_USER = os.environ["MAILGUN_SMTP_LOGIN"]
    EMAIL_HOST_PASSWORD = os.environ["MAILGUN_SMTP_PASSWORD"]
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    AWS_ACCESS_KEY_ID = os.environ["BUCKETEER_AWS_ACCESS_KEY_ID"]
    AWS_S3_REGION_NAME = os.environ["BUCKETEER_AWS_REGION"]
    AWS_SECRET_ACCESS_KEY = os.environ["BUCKETEER_AWS_SECRET_ACCESS_KEY"]
    AWS_STORAGE_BUCKET_NAME = os.environ["BUCKETEER_BUCKET_NAME"]


else:
    ALLOWED_HOSTS = ["localhost"]
    CSRF_TRUSTED_ORIGINS = []
    WEBSOCKET_SCHEME = "ws"
    HTTP_SCHEME = "https"

    EMAIL_HOST_USER = "no-reply@example.com"
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    AWS_ACCESS_KEY_ID = os.environ["MINIO_ACCESS_KEY"]
    AWS_S3_REGION_NAME = "eu-west-2"
    AWS_SECRET_ACCESS_KEY = os.environ["MINIO_SECRET_KEY"]
    AWS_STORAGE_BUCKET_NAME = os.environ["MINIO_BUCKET_NAME"]
    AWS_S3_ENDPOINT_URL = "http://localhost:9000"

    s3 = boto3.client(
        "s3",
        endpoint_url=AWS_S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    try:
        s3.create_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
    except Exception:
        pass


# Application definition

INSTALLED_APPS = [
    "django_q",
    "daphne",
    "core.apps.CoreConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

ROOT_URLCONF = "dosac.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "dosac.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_NAME"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}

UNSTRUCTURED_API_URL = os.environ["UNSTRUCTURED_API_URL"]
UNSTRUCTURED_API_KEY = os.environ["UNSTRUCTURED_API_KEY"]

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / STATIC_URL

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


ASGI_APPLICATION = "dosac.asgi.application"


AUTH_USER_MODEL = "core.User"


Q_CLUSTER = {
    "name": "DjangORM",
    "workers": 4,
    "timeout": 90,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

AUTHENTICATION_URL = "sesame/login/"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
}
