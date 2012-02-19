#-*- coding: utf-8 -*-

__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '26 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from datetime import datetime

from google.appengine.api import memcache
import logging
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

from perart.models import Program, Project, News, Image, Menu, Gallery, Settings


def index(request):
    return render_to_response('perart/cms/index.html', {'programs': Program.objects.all(),
                                                        'menu': Settings.get_main_menu(),
                                                        'news': News.objects.all().order_by('-published')[:15]},
                              context_instance=RequestContext(request))

def render_blob(title, blob):
    response = HttpResponse(blob, mimetype='image/jpeg')
    response['Content-disposition'] = 'filename="%s"' % title.encode('utf-8')
    return response


def blob(request, model, field, key):
    model = model.lower()
    if model == 'program':
        try:
            obj = Program.objects.get(pk=key)
            return render_blob(obj.title, getattr(object, field))
        except Program.DoesNotExist: pass
    raise Http404('Image not found!')


def program(request, url=None):
    program = Program.get_by_url(url)
    if program is None:
        raise Http404('Program not found!')
    return render_to_response('perart/cms/project.html', {'program': program, 'object': program},
                              context_instance=RequestContext(request))


def gallery(request, program_url, gallery_url):
    program = Program.get_by_url(program_url)
    gallery = Gallery.get_by_url(gallery_url)
    if program is None or project is None:
        raise Http404('Gallery not found!')
    return render_to_response('perart/cms/gallery.html', {'program': program, 'object': gallery},
                              context_instance=RequestContext(request))


def project(request, program_url, project_url):
    program = Program.get_by_url(program_url)
    project = Project.get_by_url(project_url)
    if program is None or project is None:
        raise Http404('Project not found!')
    return render_to_response('perart/cms/project.html', {'program': program, 'object': project},
                              context_instance=RequestContext(request))


def image(request, key, thumbnail=None):
    try:
        image = Image.objects.get(pk=key)
        if thumbnail == 'thumbnail':
            return render_blob(image.gallery.title, image.thumbnail)
        else:
            return render_blob(image.gallery.title, image.image)
    except Image.DoesNotExist:
        raise Http404('Image not found!')


def news(request, url=None):
    all_news = News.objects.order_by('-published')
    if url is None:
        news = all_news[0]
    else:
        news = News.get_by_url(url)
    return render_to_response('perart/cms/news.html', {'object': news, 'news': all_news, 'programs': Program.objects.all()},
                              context_instance=RequestContext(request))


#def image(request, size, key):
#    image = Media.get_image(key, size)
#    if image:
#        response = HttpResponse(image.file if size == 'full' else image.thumbnail, mimetype='image/jpeg')
#        response['Content-disposition'] = 'filename="%s"' % str(image.name)
#        return response
#    else:
#        raise Http404('Image not found!')


#def media(request, key, name):
#    '''Forces download of selected file'''
#    media = Media.get_media(key)
#    if media:
#        response = HttpResponse(media.file, mimetype='application/octet-stream')
#        response['Content-disposition'] = 'attachment; filename="%s"' % str(media.name)
#        return response
#    else:
#        raise Http404('Media not found!')
#
#
#def feed(request):
#    '''Handler for RSS feed, displays the last 10 added pages'''
#    # Sat, 08 Aug 2009 12:57:53 +0000
#    fmt = '%a, %d %b %Y %H:%M:%S +0000'
#    items = memcache.get('feed') #@UndefinedVariable
#    if items is None:
#        items = []
#        query = Page.gql('WHERE draft = :1 ORDER BY created DESC', False)
#        for page in query:
#            item = {
#                'title':page.title,
#                'content': page.content,
#                'url': page.url,
#                'date':page.created.strftime(fmt)
#            }
#            items.append(item)
#        memcache.set('feed',items) #@UndefinedVariable
#    if len(items):
#        pubdate = items[0]['date']
#    else:
#        pubdate = datetime.utcnow().strftime(fmt)
#
#    data = {
#        'domain'  : request.META.get('HTTP_HOST'),
#        'pubdate' : pubdate,
#        'items'   : items
#    }
#    return render_to_response('perart/feed.html', data, mimetype='application/rss+xml; Charset=utf-8',
#                              context_instance=RequestContext(request))
