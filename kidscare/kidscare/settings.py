"""
Django settings for kidscare project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import socket
if socket.gethostname() == 'iZ23otdlkscZ':
    RunInCloud = True
else:
    RunInCloud = False
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xwzfgeu=ue3$4t!rj1!bq1%gaq=3ecwd&@06y8qc=m&%ui9jbb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    #'django.contrib.staticfiles',
    'kidscare.mombabyprods',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kidscare.urls'

WSGI_APPLICATION = 'kidscare.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
if RunInCloud:
   DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mom_baby',
            'USER': 'spider',
            'PASSWORD': 'wodemima',
            'HOST': 'alikidscare.mysql.rds.aliyuncs.com',
            'PORT': '3306'
        }
    }
else:
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mom_baby',
            'USER': 'spider',
            'PASSWORD': 'wodemima',
            'HOST': '127.0.0.1',
            'PORT': '3306'
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_DIR = os.path.join(BASE_DIR, 'static/templates')

PROFILE_LOG_BASE = os.path.join(BASE_DIR, 'log/profilings/')

if RunInCloud:
    MOMBABY_HOST = '121.40.99.4'
    DbHost = 'alikidscare.mysql.rds.aliyuncs.com'
else:
    MOMBABY_HOST = '10.31.186.63:8004'
    DbHost = '10.31.186.63'
    
