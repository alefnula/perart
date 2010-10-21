__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from django.conf.urls.defaults import *

urlpatterns = patterns('perart.views',
    url(r'^admin/', include('perart.urls.urls_admin')),
    url(r'^',       include('perart.urls.urls_cms')),
)
