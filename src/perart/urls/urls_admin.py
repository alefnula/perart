__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from django.conf.urls.defaults import *
from django.views.generic import simple

from tea.gae.decorators import admin_required

from perart import forms
from perart.models import Program, Project, News, Menu, Gallery

urlpatterns = patterns('perart.views',
    # Admin interface
    url(r'^$', admin_required(simple.redirect_to), {'url': 'projects/'}, name='perart.admin_main'),
    # List views
    url(r'^programs/$', 'admin.object_list', {'queryset': Program.objects.all}, name='perart.admin.program.list'),
    url(r'^projects/$', 'admin.object_list', {'queryset': Project.objects.all}, name='perart.admin.project.list'),
    url(r'^news/$',     'admin.object_list', {'queryset': News.objects.all},    name='perart.admin.news.list'),
    url(r'^gallery/$',  'admin.object_list', {'queryset': Gallery.objects.all}, name='perart.admin.gallery.list'),
    url(r'^menu/$',     'admin.object_list', {'queryset': Menu.objects.all},    name='perart.admin.menu.list'),
    
    # Edit views
    url(r'^program-edit/(?:(?P<id>\d+)/)?$', 'admin.object_edit',
            {'model': Program, 'form': forms.ProgramForm, 'extra_content': {'page': 'program'}},
            name='perart.admin.program.edit'),
    url(r'^project-edit/(?:(?P<id>\d+)/)?$', 'admin.object_edit',
            {'model': Project, 'form': forms.ProjectForm, 'extra_content': {'page': 'project'}},
            name='perart.admin.project.edit'),
    url(r'^news-edit/(?:(?P<id>\d+)/)?$',    'admin.object_edit',
            {'model': News,    'form': forms.NewsForm,     'extra_content': {'page': 'news'}},
            name='perart.admin.news.edit'),
    url(r'^menu-edit/(?:(?P<id>\d+)/)?$',    'admin.object_edit',
            {'model': Menu,    'form': forms.MenuForm,     'extra_content': {'page': 'menu'}},
            name='perart.admin.menu.edit'),

    # Delete views
    url(r'^program-delete/(?P<id>\d+)/$', 'admin.object_delete', {'model': Program}, name='perart.admin.program.delete'),
    url(r'^project-delete/(?P<id>\d+)/$', 'admin.object_delete', {'model': Project}, name='perart.admin.project.delete'),
    url(r'^news-delete/(?P<id>\d+)/$',    'admin.object_delete', {'model': News},    name='perart.admin.news.delete'),
    url(r'^gallery-delete/(?P<id>\d+)/$', 'admin.object_delete', {'model': Gallery}, name='perart.admin.gallery.delete'),
    url(r'^menu-delete/(?P<id>\d+)/$',    'admin.object_delete', {'model': Menu},    name='perart.admin.menu.delete'),

    # Gallery
    url(r'^gallery-edit/(?:(?P<id>\d+)/)?$',    'admin.gallery.edit',         name='perart.admin.gallery.edit'),
    url(r'^gallery-upload-image/(?P<id>\d+)/$', 'admin.gallery.upload_image', name='perart.admin.gallery.upload_image'),    
    url(r'^gallery-remove-image/$',             'admin.gallery.remove_image', name='perart.admin.gallery.remove_image'),

    # Program
    url(r'^program-menu-edit/(?:(?P<key>[\w-]+)/)?$', 'admin.program_menu_edit', name='perart.admin.program.menu_edit'),
    
    # Settings
    url(r'^settings-main-page-edit/', 'admin.settings.main_page_edit', name='perart.admin.settings.main_page_edit'),
    # Media admin
    #url(r'^upload/$',       'admin.media_upload',   name='perart.admin_media_upload'),
    #url(r'^remove-media/$', 'admin.media_remove',   name='perart.admin_media_remove'),
    #url(r'^site/$',         'admin.site',           name='perart.admin_site'),
)
