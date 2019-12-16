# -*- coding: utf-8 -*-
from settings import *

DEBUG = False
TEMPLATE_DEBUG = False

SITE_NAME = '%(titulo)s'
SITE_HOST = 'http://%(host)s'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%(dbname)s',
        'USER': '%(dbuser)s',
        'PASSWORD': '%(dbpassword)s',
        'HOST': '%(dbhost)s',
        'PORT': '',
    },
}

ALLOWED_HOSTS = ['%(host)s', 'www.%(host)s', ]

INSTALLED_APPS +=(
    'django.contrib.staticfiles',
    'theme',
)

REPLY_TO_EMAIL = u'%(from)s'
DEFAULT_FROM_EMAIL = u'%(from)s'