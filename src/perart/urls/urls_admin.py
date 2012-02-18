__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from django.conf.urls.defaults import *
from django.views.generic import simple

from tea.gae.decorators import admin_required

from perart import forms
from perart import models

urlpatterns = patterns('perart.views',
    # Admin interface
    url(r'^$', admin_required(simple.redirect_to), {'url': 'projects/'}, name='perart.admin_main'),
    # List views
    url(r'^programs/$', 'admin.object_list', {
            'queryset'      : models.Program.objects.all,
            'template_name' : 'perart/admin/program_list.html',
            'extra_content' : {'page': 'program'}
    }, name='perart.admin_program_list'),
    url(r'^projects/$', 'admin.object_list', {
            'queryset'      : models.Project.objects.all,
            'template_name' : 'perart/admin/project_list.html',
            'extra_content' : {'page': 'project'}
    }, name='perart.admin_project_list'),
    url(r'^news/$',     'admin.object_list', {
            'queryset'      : models.News.objects.all,
            'template_name' : 'perart/admin/news_list.html',
            'extra_content' : {'page': 'news'}
    }, name='perart.admin_news_list'),
    url(r'^gallery/$',  'admin.object_list', {
            'queryset'      : models.Gallery.objects.all,
            'template_name' : 'perart/admin/gallery_list.html',
            'extra_content' : {'page': 'gallery'}
    }, name='perart.admin_gallery_list'),
    
    # Edit views
    url(r'^program-edit/(?:(?P<key>[\w-]+)/)?$', 'admin.object_edit',
            {'model': models.Program, 'form': forms.ProgramForm, 'extra_content': {'page': 'program'}},
            name='perart.admin_program_edit'),
    url(r'^project-edit/(?:(?P<key>[\w-]+)/)?$', 'admin.object_edit',
            {'model': models.Project, 'form': forms.ProjectForm, 'extra_content': {'page': 'project'}},
            name='perart.admin_project_edit'),
    url(r'^news-edit/(?:(?P<key>[\w-]+)/)?$',    'admin.object_edit',
            {'model': models.News,    'form': forms.NewsForm,     'extra_content': {'page': 'news'}},
            name='perart.admin_news_edit'),

    # Remove views
    url(r'^program-remove/(?P<key>[\w-]+)/$', 'admin.object_remove', {'model': models.Program},
            name='perart.admin_program_remove'),
    url(r'^project-remove/(?P<key>[\w-]+)/$', 'admin.object_remove', {'model': models.Project},
            name='perart.admin_project_remove'),
    url(r'^news-remove/(?P<key>[\w-]+)/$',    'admin.object_remove', {'model': models.News},
            name='perart.admin_news_remove'),
    url(r'^gallery-remove/(?P<key>[\w-]+)/$', 'admin.object_remove', {'model': models.Gallery},
            name='perart.admin_gallery_remove'),

    # Gallery
    url(r'^gallery-edit/(?:(?P<key>[\w-]+)/)?$',         'admin.gallery.gallery_edit',
        name='perart.admin_gallery_edit'),
    url(r'^gallery-upload-image/(?:(?P<key>[\w-]+)/)?$', 'admin.gallery.upload_image',
        name='perart.admin_gallery_upload_image'),    
    url(r'^gallery-remove-image/$',                      'admin.gallery.remove_image',
        name='perart.admin_gallery_remove_image'),

    # Program
    url(r'^program-menu-edit/(?:(?P<key>[\w-]+)/)?$', 'admin.program_menu_edit',
        name='perart.admin_program_menu_edit'),
    
    # Settings
    url(r'^settings-main-menu-edit/', 'admin.settings.main_menu_edit',
        name='perart.admin_settings_main_menu_edit'),
    # Media admin
    #url(r'^upload/$',       'admin.media_upload',   name='perart.admin_media_upload'),
    #url(r'^remove-media/$', 'admin.media_remove',   name='perart.admin_media_remove'),
    #url(r'^site/$',         'admin.site',           name='perart.admin_site'),
)
