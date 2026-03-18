"""
Django settings for lawfirm project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def get_required_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    raise ImproperlyConfigured(
        f"One of the environment variables {', '.join(names)} must be set for database configuration."
    )


# ── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-only-change-me')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]


# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',

    # Propias
    'apps.core',
    'apps.security',
    'apps.penalcode',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'lawfirm.urls'


# ── Templates ─────────────────────────────────────────────────────────────────
# DIRS   → templates raíz del proyecto  (base.html, components/, core/, etc.)
# APP_DIRS → True activa la búsqueda automática en <app>/templates/ de cada app
#            registrada en INSTALLED_APPS (segurity/templates/, penalcode/templates/, …)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← carpeta raíz del proyecto
        'APP_DIRS': True,                   # ← activa <app>/templates/ automáticamente
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

WSGI_APPLICATION = 'lawfirm.wsgi.application'


# ── Base de datos ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME':     get_required_env('DB_NAME', 'DB_DATABASE'),
        'USER':     get_required_env('DB_USER', 'DB_USERNAME'),
        'PASSWORD': get_required_env('DB_PASSWORD'),
        'HOST':     get_required_env('DB_HOST', 'DB_SOCKET'),
        'PORT':     os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}


# ── Validación de contraseñas ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-ec'
TIME_ZONE     = 'America/Guayaquil'
USE_I18N      = True
USE_TZ        = True


# ── Archivos estáticos ────────────────────────────────────────────────────────
#
#   Cómo funciona la búsqueda de archivos estáticos en Django:
#
#   1. django.contrib.staticfiles busca en STATICFILES_DIRS (directorios globales).
#   2. Con APP_DIRS=True en TEMPLATES ya cubrimos templates por app.
#      Para static, el finder equivalente es AppDirectoriesFinder, que busca
#      automáticamente en <app>/static/ de cada app en INSTALLED_APPS.
#      AppDirectoriesFinder ya está incluido por defecto en STATICFILES_FINDERS,
#      así que NO hay que declararlo manualmente.
#
#   Estructura resultante:
#
#   lawfirm/
#   ├── static/                ← archivos globales (favicon, fuentes propias…)
#   ├── apps/
#   │   ├── core/
#   │   │   └── static/
#   │   │       └── core/      ← siempre namespaced para evitar colisiones
#   │   │           └── css/main.css
#   │   ├── security/
#   │   │   └── static/
#   │   │       └── security/
#   │   └── penalcode/
#   │       └── static/
#   │           └── penalcode/
#   └── staticfiles/           ← destino de `collectstatic` (no versionar)
#
STATIC_URL  = '/static/'
MEDIA_URL   = '/media/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',       # archivos estáticos globales del proyecto
]

# collectstatic junta todo aquí (no incluir en STATICFILES_DIRS)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT  = BASE_DIR / 'media'

# Finders usados por Django (orden importa: primero FileSystemFinder, luego AppDirectoriesFinder)
# Estos son los valores por defecto; se declaran explícitamente para mayor claridad.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',    # busca en STATICFILES_DIRS
    'django.contrib.staticfiles.finders.AppDirectoriesFinder', # busca en <app>/static/
]


# ── Modelo de usuario personalizado ──────────────────────────────────────────
AUTH_USER_MODEL = 'security.User'


# ── Autenticación: rutas de login / logout / redirect ────────────────────────
#
#   LOGIN_URL          → a dónde redirige @login_required y LoginRequiredMixin
#                        cuando el usuario no está autenticado.
#   LOGIN_REDIRECT_URL → a dónde va el usuario DESPUÉS de hacer login
#                        si no hay un parámetro ?next= en la URL.
#   LOGOUT_REDIRECT_URL→ a dónde va el usuario DESPUÉS de hacer logout.
#
LOGIN_URL           = '/security/login/'
LOGIN_REDIRECT_URL  = '/'               # core:home
LOGOUT_REDIRECT_URL = '/security/login/'


# ── Mensajes: mapear 'error' → clase CSS 'danger' (Bootstrap / nuestro CSS) ──
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.DEBUG:   'debug',
    message_constants.INFO:    'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR:   'danger',   # ← base.html espera 'danger', no 'error'
}


# ── Default primary key ───────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'