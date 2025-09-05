import environ
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Criar o objeto Env e carregar o .env
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Variáveis do Django
SECRET_KEY = env("SECRET_KEY", default="sua_chave_padrão_se_não_existir_no_env")
DEBUG = env.bool("DEBUG", default=False)

# Configuração do banco (se estiver usando DATABASE_URL)


# Configurações ODBC
ODBC_DRIVER = env("ODBC_DRIVER", default="SQL Anywhere 17")
ODBC_SERVER = env("ODBC_SERVER", default="srvcontabil")
ODBC_DATABASE = env("ODBC_DATABASE", default="contabil")
ODBC_USER = env("ODBC_USER", default="EXTERNO")
ODBC_PASSWORD = env("ODBC_PASSWORD", default="externo")


ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "odbc_reader",
    "get_empresas",
    "get_usuarios",
    "get_folha",
    "get_main_pages",
    "authenticator",
    "get_api_token",
    "drf_spectacular",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# Permitir CORS de qualquer origem (caso precise ser mais restritivo, pode alterar isso)
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "setup.urls"

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

WSGI_APPLICATION = "setup.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "setup.authentication.BodyTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Gestão Office API",
    "DESCRIPTION": "Documentação automática e interativa da API",
    "VERSION": "1.0.0",
    # ↓↓↓↓ ESSAS CONFIGURAÇÕES VÃO SILENCIAR TUDO ↓↓↓↓
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "ENUM_NAME_OVERRIDES": {},
    "GENERIC_ADDITIONAL_PROPERTIES": None,
    "SCHEMA_PATH_PREFIX": None,
    "AUTHENTICATION_WHITELIST": [],  # Ignora TODAS as classes de autenticação
    "PREPROCESSING_HOOKS": [
        "drf_spectacular.hooks.preprocess_exclude_path_format"  # Ignora erros de paths
    ],
    "DISABLE_ERRORS_AND_WARNINGS": True,  # ←⭐ ISSO AQUI É O MAIS IMPORTANTE!
    "SWAGGER_UI_SETTINGS": {
        "displayOperationId": True,
        "filter": True,
        "deepLinking": True,
        "persistAuthorization": True,
        "security": [],  # Remove o cadeado da UI
    },
}

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
