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
def object_list(request, queryset, template_name='perart/admin/object_list.html', extra_content=None):
    data       = {} if extra_content is None else extra_content.copy()
    model      = queryset.im_self.model().__class__
    model_name = model.__name__
    data.update({
        'object_list' : queryset(),
        'model'       : model,
        'model_name'  : model_name,
        'page'        : model_name.lower(),
    })
    return render_to_response(template_name, data, context_instance=RequestContext(request))


@admin_required
def object_edit(request, model, form, template='perart/admin/object_edit.html', extra_content=None, id=None):
    try:
        obj = model.objects.get(pk=id) if id is not None else None
    except model.DoesNotExist:
        raise Http404('%s not found' % model.__name__)
    if request.method == 'GET':
        f = form(instance=obj)
    if request.method == 'POST':
        f = form(request.POST, files=request.FILES, instance=obj)
        if f.is_valid():
            obj = f.save()
            if hasattr(obj, 'create_thumbnail'):
                obj.create_thumbnail()
                obj.save()
            return HttpResponseRedirect(model.get_list_url() + ('?saved=%s' % obj.id))
    data = {} if extra_content is None else extra_content.copy()
    data.update({'form': f, 'object': object, 'model': model})
    return render_to_response(template, data, context_instance=RequestContext(request))


@admin_required
def object_delete(request, model, id):
    obj = model.objects.get(pk=id)
    if not obj:
        raise Http404('%s not found' % model.__name__)
    obj.delete()
    return HttpResponseRedirect(model.get_list_url() + '?removed=true')
