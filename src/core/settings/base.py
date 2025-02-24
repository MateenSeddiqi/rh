import os
import sys
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR.parent, ".env"))

SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key")

DJANGO_SETTINGS_MODULE = env("DJANGO_SETTINGS_MODULE", default="core.settings.local")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=True)
APP_NAME = env("APP_NAME", default="ReportHub")

# Application definition
INSTALLED_APPS = [
    # Default django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Installed packages apps
    "django_filters",
    "django_htmx",
    "dbbackup",
    "extra_settings",
    "mdeditor",
    "mailer",
    "django_extensions",
    # RH apps
    "rh.apps.RhConfig",
    "users.apps.UsersConfig",
    "stock.apps.StockConfig",
    "project_reports.apps.ProjectReportsConfig",
    "guides.apps.GuidesConfig",
]
USE_DJANGO_JQUERY = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.MaintenanceModeMiddleware",
    "core.middleware.HtmxMessageMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "rh.context_processors.env_variables",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50240


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "users.backends.EmailBackend",
]

# Guadian Anonymous User
ANONYMOUS_USER_ID = -1

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "static-cdn"

# Base URL to serve media files
MEDIA_URL = "/media/"

# Directory where media files are stored
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/profile/"
LOGOUT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

TESTING = "test" in sys.argv

EXTRA_SETTINGS_DEFAULTS = [
    {
        "name": "MAINTENANCE_MODE_ENABLED",
        "type": "bool",
        "value": False,
    },
    {
        "name": "MAINTENANCE_MODE_IGNORE_SUPERUSER",
        "type": "bool",
        "value": True,
        "description": "if True the superuser will not see the maintenance-mode page",
    },
    {
        "name": "MAINTENANCE_MODE_IGNORE_STAFF",
        "type": "bool",
        "value": True,
        "description": "if True the staff will not see the maintenance-mode page",
    },
    {
        "name": "MAINTENANCE_MODE_REDIRECT_ROUTE",
        "type": "string",
        "value": "maintenance",
        "description": "if True the staff will not see the maintenance-mode page",
    },
    {
        "name": "MAINTENANCE_BYPASS_QUERY",
        "type": "string",
        "value": "godmode",
        "description": "secret code to bypass maintenance mode for the user, ex: reporthub.immap.org/?godmode",
    },
    {
        "name": "RECORDS_PER_PAGE",
        "type": "int",
        "value": 10,
        "description": "No of items in a paginated results.",
    },
]

# MDEditor
X_FRAME_OPTIONS = "SAMEORIGIN"
MEDIA_URL = "/media/"
MDEDITOR_CONFIGS = {
    "default": {
        "width": "100% ",  # Custom edit box width
        # "height": 200,  # Custom edit box height
        "imageUpload": True,
        "upload_image_formats": [
            "jpg",
            "jpeg",
            "gif",
            "png",
            "bmp",
            "webp",
        ],  # image upload format type
        "image_folder": "editor",  # image save the folder name
        "theme": "dark",  # edit box theme, dark / default
        "preview_theme": "dark",  # Preview area theme, dark / default
        "editor_theme": "pastel-on-dark",  # edit area theme, pastel-on-dark / default
        "toolbar_autofixed": True,  # Whether the toolbar capitals
        "search_replace": True,  # Whether to open the search for replacement
        "emoji": True,  # whether to open the expression function
        "tex": True,  # whether to open the tex chart function
        "flow_chart": True,  # whether to open the flow chart function
        "sequence": True,  # Whether to open the sequence diagram function
        "watch": True,  # Live preview
        "lineWrapping": False,  # lineWrapping
        "lineNumbers": True,  # lineNumbers
        "language": "en",  # zh / en / es
    }
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR.parent / "rh-django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
