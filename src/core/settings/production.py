# ruff: noqa
import sentry_sdk

from .base import *

APP_ENV = env("APP_ENV", default="production")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "dev.reporthub.immap.org"]

SENTRY_DSN = env("SENTRY_DSN", default="")

if APP_ENV == "production":
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        send_default_pii=True,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.6,
    )


DATABASES = {
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="rh"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="admin"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    },
}

DB = env("DB", default="sqlite")

DATABASES["default"] = DATABASES[DB]


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
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


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

DJANGO_VITE_PLUGIN = {
    "BUILD_DIR": "static-cdn/build",
    "BUILD_URL_PREFIX": "/" + STATIC_URL + "build",
    "DEV_MODE": False,
    "STATIC_LOOKUP": False,
}

# Backup to DropBox
DBBACKUP_STORAGE = "storages.backends.dropbox.DropBoxStorage"
DBBACKUP_SEND_EMAIL = False
DBBACKUP_STORAGE_OPTIONS = {
    "oauth2_access_token": env("DROPBOX_ACCESS_TOKEN", default=""),
    "oauth2_refresh_token": env("DROPBOX_REFRESH_TOKEN", default=""),
    "app_key": env("DROPBOX_APP_KEY", default=""),
    "app_secret": env("DROPBOX_APP_SECRET", default=""),
}


# Can use MailTrap SMTP Setup for now (dev and staging only).
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "mailer.backend.DbBackend"

EMAIL_HOST = env("EMAIL_HOST", default="smtp.mailtrap.io")
EMAIL_PORT = env("EMAIL_PORT", default=587)  # 2525
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="reporthub@immap.org")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="reporthub@immap.org")
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
