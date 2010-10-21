__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from django.conf.urls.defaults import *

urlpatterns = patterns('perart.views',
    url(r'^$',                                                     'cms.index',       name='perart.index'),
    url(r'^blob/(?P<model>\w+)/(?P<field>\w+)/(?P<key>[\w-]+)/$',  'cms.blob',        name='perart.blob'),
    url(r'^news/(?:(?P<url>[\w-]+)/)?$',                           'cms.news',        name='perart.news'),
    url(r'^image/(?P<key>[\w-]+)/(?:(?P<thumbnail>thumbnail)/)?$', 'cms.image',       name='perart.image'),
    url(r'^(?P<url>[\w-]+)/$',                                     'cms.program',     name='perart.program'),
    url(r'^(?P<program_url>[\w-]+)/g/(?P<gallery_url>[\w-]+)/$',   'cms.gallery',     name='perart.gallery'),
    url(r'^(?P<program_url>[\w-]+)/(?P<project_url>[\w-]+)/$',     'cms.project',     name='perart.project'),
#    url(r'^download/(.*)/(.*)/$',  'cms.media',        name='perart.media'),
#    url(r'^feed/$',                'cms.feed',         name='perart.feed'),
)
