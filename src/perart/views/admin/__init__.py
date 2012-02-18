__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '26 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import logging

from google.appengine.api import images
from google.appengine.api import memcache

from django.utils import simplejson
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect

from tea.gae.decorators import admin_required
from perart.models import Program, Project, News, Image, Menu
from perart.forms import ProgramForm, ProjectForm, NewsForm

# Admin interface

@admin_required
def object_list(request, queryset, template_name, extra_content=None):
    data = {} if extra_content is None else extra_content.copy()
    data['object_list'] = queryset()
    return render_to_response(template_name, data, context_instance=RequestContext(request))


@admin_required
def object_edit(request, model, form, template='perart/admin/object_edit.html', extra_content=None, key=None):
    obj = model.objects.get(pk=key) if key is not None else None
    if request.method == 'GET':
        f = form(instance=obj)
    if request.method == 'POST':
        f = form(request.POST, files=request.FILES, instance=obj)
        if f.is_valid():
            obj = f.save()
            return HttpResponseRedirect(model.get_list_url() + ('?saved=%s' % str(obj.key())))
    data = {} if extra_content is None else extra_content.copy()
    data.update({'form': f, 'object': obj, 'model': model})
    return render_to_response(template, data, context_instance=RequestContext(request))


@admin_required
def object_with_image_edit(request, model, form, images=None, template='perart/admin/object_edit.html', extra_content=None, key=None):
    obj = model.objects.get(pk=key) if key is not None else None
    if request.method == 'GET':
        f = form(instance=obj)
    if request.method == 'POST':
        f = form(request.POST, files=request.FILES, instance=obj)
        if f.is_valid():
            obj = f.save()
            if hasattr(obj, 'create_thumbnail'):
                obj.create_thumbnail()
                obj.save()
            return HttpResponseRedirect(model.get_list_url() + ('?saved=%s' % str(obj.key())))
    data = {} if extra_content is None else extra_content.copy()
    data.update({'form': f, 'object': object, 'model': model})
    return render_to_response(template, data, context_instance=RequestContext(request))


@admin_required
def object_remove(request, model, key):
    obj = model.objects.get(pk=key)
    if not obj:
        raise Http404('%s not found' % model.__name__)
    obj.delete()
    return HttpResponseRedirect(model.get_list_url() + '?removed=true')



def program_menu_edit(request, key):
    program = Program.objects.get(pk=key)
    if not program:
        raise Http404('Program not found')        
    if request.method == 'POST':
        program.menu = request.POST.get('menu', '')
        try:
            program.get_menu(use_cache=False)
        except Exception, error:
            return render_to_response('perart/admin/program_menu_edit.html', {'program': program, 'error': error}, 
                                      context_instance=RequestContext(request))
        program.put()
        return HttpResponseRedirect(Program.get_list_url())
    return render_to_response('perart/admin/program_menu_edit.html', {'program': program}, 
                              context_instance=RequestContext(request))       
