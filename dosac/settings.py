import os
from logging import getLogger
from pathlib import Path

import boto3
from dotenv import load_dotenv

logger = getLogger(__name__)

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

    CORS_ALLOWED_ORIGIN_REGEXES = [f"https://{APP_HOST}"]

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    CORS_CONFIGURATION = {
        "CORSRules": [
            {
                "AllowedHeaders": ["*"],
                "ExposeHeaders": ["ETag", "x-amz-meta-custom-header"],
                "AllowedMethods": ["HEAD", "GET", "PUT", "POST", "DELETE"],
                "AllowedOrigins": ["*"],
            }
        ]
    }
    put_bucket_cors_result = s3.put_bucket_cors(
        Bucket=AWS_STORAGE_BUCKET_NAME, CORSConfiguration=CORS_CONFIGURATION
    )
    logger.info(put_bucket_cors_result)


else:
    ALLOWED_HOSTS = ["localhost"]
    CSRF_TRUSTED_ORIGINS = []
    WEBSOCKET_SCHEME = "ws"
    HTTP_SCHEME = "http"

    EMAIL_HOST_USER = "no-reply@example.com"
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    AWS_S3_REGION_NAME = "eu-west-2"
    if "MINIO_ACCESS_KEY" in os.environ:
        AWS_ACCESS_KEY_ID = os.environ["MINIO_ACCESS_KEY"]
        AWS_SECRET_ACCESS_KEY = os.environ["MINIO_SECRET_KEY"]
        AWS_STORAGE_BUCKET_NAME = os.environ["MINIO_BUCKET_NAME"]
        minio_host = os.environ["MINIO_HOST"]
        minio_port = os.environ["MINIO_PORT"]
        AWS_S3_ENDPOINT_URL = f"http://{minio_host}:{minio_port}"
    else:
        AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
        AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
        AWS_S3_ENDPOINT_URL = os.environ["AWS_S3_ENDPOINT_URL"]

    s3 = boto3.client(
        "s3",
        endpoint_url=AWS_S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    CORS_ALLOW_ALL_ORIGINS = True

    try:
        s3.create_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
    except Exception:
        pass


AWS_S3_SIGNATURE_VERSION = "s3v4"

# Application definition

INSTALLED_APPS = [
    "django_q",
    "daphne",
    "corsheaders",
    "core.apps.CoreConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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

logger.info("DATABASES=%", DATABASES)

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
    "max_attempts": 1,
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
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}
