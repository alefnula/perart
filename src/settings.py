__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import os
from djangoappengine.settings_base import *

PROJECT_DIR  = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Viktor Kerkez', 'alefnula@gmail.com'),
)
MANAGERS = ADMINS

#PERART_EMAIL = 'alefnula@gmail.com'
PERART_EMAIL = 'office@perart.org'

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'indexes'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hvhxfm5u=^*v&doo#oq8x*eg8+1&9sxbye@=umutgn^t_sg_nx'

# Ensure that email is not sent via SMTP by default to match the standard App
# Engine SDK behaviour. If you want to sent email via SMTP then add the name of
# your mailserver here.
EMAIL_HOST = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.doc.XViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'perart.context_processors.cms_data',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates')
)

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
    'tea.django',
    'perart',
)


TINY_MCE_SETTINGS =  '''
script_url: '/static/js/tiny_mce/tiny_mce.js',
theme: 'advanced',
plugins: 'advimage,tabfocus,inlinepopups,preview,media',

theme_advanced_buttons1: 'undo,redo,|,bold,italic,underline,strikethrough,|,image,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,blockquote,link,hr,|,forecolor,backcolor,|,code,preview,',
theme_advanced_buttons2: 'formatselect,fontselect,fontsizeselect,media',
theme_advanced_buttons3: null,
theme_advanced_buttons4: null,
  
theme_advanced_toolbar_location: 'top',
theme_advanced_toolbar_align: 'left',
theme_advanced_statusbar_location: 'bottom',
theme_advanced_resizing: true,
relative_urls: false,

content_css : '/static/css/tiny_mce.css',

extended_valid_elements: "iframe[src|width|height|name|align]",
'''
