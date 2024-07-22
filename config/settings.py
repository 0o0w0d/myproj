"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import sys
from pathlib import Path
from environ import Env
from django.core.exceptions import ImproperlyConfigured


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()

ENV_PATH = Path(env.str("ENV_PATH", default=str(BASE_DIR / ".env")))

if ENV_PATH.exists():
    with ENV_PATH.open(encoding="utf-8") as f:
        env.read_env(f, overwrite=True)
else:
    print("not found:", ENV_PATH, file=sys.stderr)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-dn^kymsy5h(e&jtgba0r#jh1v6!9gao1e2#g!5#76b)5=dh2s)",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

# django service domain
# 포트 번호를 제외한 도메인 입력
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["api.mydj.com"])


CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


# Application definition

INSTALLED_APPS = [
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "django.contrib.staticfiles",
    "django_components.safer_staticfiles",
    # third apps
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_components",
    "django_extensions",
    "template_partials",
    "django_htmx",
    "rest_framework",
    "taggit",
    # local apps
    "core",
    "accounts",
    "photolog",
    "blog",
]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
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
    "django_htmx.middleware.HtmxMiddleware",
]

if DEBUG:
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [  # add django-component management path
            BASE_DIR / "core" / "src-django-components",
        ],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"


DATABASES = {
    "default": env.db(default=DEFAULT_DATABASE_URL),
}

# Custom User model
AUTH_USER_MODEL = "accounts.User"


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

LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="ko-kr")

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = env.str("STATIC_URL", default="djstatic/")

STATIC_ROOT = env.str("STATIC_ROOT", default=BASE_DIR / "staticfiles")

STATICFILES_DIRS = [
    BASE_DIR / "core" / "src-django-components",
]


# media files

MEDIA_URL = env.str("MEDIA_URL", default="media/")

MEDIA_ROOT = env.str("MEDIA_ROOT", default=BASE_DIR / "mediafiles")


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# django-debug-toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html

INTERNAL_IPS = env.list("INTERNAL_IPS", default=["127.0.0.1"])


# django-taggit

TAGGIT_CASE_INSENSITIVE = env.bool("TAGGIT_CASE_INSENSITIVE", default=True)


# django-crispy-forms

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"


# django-components config ( context variable handling )

COMPONENTS = {"slot_context_behavior": "allow_override"}  # default: "prefer_root"


# email config
EMAIL_HOST = env.str("EMAIL_HOST", default=None)

if DEBUG and EMAIL_HOST is None:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    try:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        EMAIL_PORT = env.int("EMAIL_PORT")
        EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
        EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
        EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
        EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
        DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
    except ImproperlyConfigured as e:
        print("ERROR:", e, file=sys.stderr)
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# django-rest-framework
# https://www.django-rest-framework.org

REST_FRAMEWORK = {
    #     # Use Django's standard `django.contrib.auth` permissions,
    #     # or allow read-only access for unauthenticated users.
    #     "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # renderer 설정 (default: json+browser, pandasxlsx+wordcloud)
    # renderer 설정 시, 각각 api마다 설정 가능
    # (FBV -> rest_framework.decorators.renderer_classes / CBV -> renderer_classes 속성 클래스 내부 구현)
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "core.renderers.PandasXlsxRenderer",
        "core.renderers.WordcloudRenderer",
    ],
    # paging 설정
    "PAGE_SIZE": env.int("REST_FRAMEWORK_PAGE_SIZE", default=5),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # ListModelMixin class를 상속받은 모든 API 뷰에 페이지네이션 처리
}


# django-cors-headers
# https://github.com/adamchainz/django-cors-headers

# CORS 허용 주소
# CorsMiddleware를 통해 응답 헤더에 Access-Control-Allow-Origin로 아래 주소 추가
# http/https 스키마 및 포트 번호를 포함한 전체 주소
CORS_ALLOWED_ORIGINS = ["http://mydj.com:3000"]


# 다른 출처로부터의 요청에 쿠키 자동 전송 허용 여부
# 응답 헤더에 Access-Control-Allow-Credentials=true 추가
CORS_ALLOW_CREDENTIALS = True

# 지정 도메인에서 서브 도메인 포함하여 세션 쿠키 공유 설정
#    -> sessionid 쿠키 생성 시 domain 속성으로 지정해 브라우저에서 서브 도메인 간에 쿠키 공유
SESSION_COOKIE_DOMAIN = ".mydj.com"
