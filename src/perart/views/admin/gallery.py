__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '16 May 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import logging

from django.utils import simplejson
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect

from tea.gae.decorators import admin_required

from perart.models import Gallery, Image
from perart.forms import GalleryForm


@admin_required
def gallery_edit(request, key=None):
    object = Gallery.get(key) if key is not None else None
    if request.method == 'GET':
        f = GalleryForm(instance=object)
    if request.method == 'POST':
        f = GalleryForm(request.POST, files=request.FILES, instance=object)
        if f.is_valid():
            object = f.save()
            return HttpResponseRedirect(Gallery.get_list_url() + ('?saved=%s' % str(object.key())))
    if object is not None:
        images = simplejson.dumps(map(lambda x: {'key': str(x.key()), 'thumbnail' : x.thumbnail_url()}, list(object.image_set)))
    else:
        images = simplejson.dumps([])
    data = {'form': f, 'images': images,
            'object': object, 'model': Gallery, 'page': 'gallery'}
    return render_to_response('perart/admin/gallery_edit.html', data, context_instance=RequestContext(request))


@admin_required
def upload_image(request, key):
    gallery = Gallery.get(key)
    if request.method == 'POST':
        MAX_FILE_SIZE = 1048576
        data = { 'status': '', 'key': '', 'thumbnail': ''}
        if not 'file' in request.FILES or request.FILES.get('file').size > MAX_FILE_SIZE:
            data['status'] = 'ERROR'
            return render_to_response('teacupcms/upload_response.html', data, context_instance=RequestContext(request))
        image = Image(gallery=gallery)
        try:
            image.image = request.FILES.get('file').read()
            image.create_thumbnail()
            image.put()
        except:
            logging.exception('Exception in saving image...')
        data.update({'status': 'OK', 'key': str(image.key()), 'thumbnail': image.thumbnail_url()})
        return render_to_response('perart/admin/upload_response.html', data, context_instance=RequestContext(request))
    else:
        raise Http404('Invalid request method!')


@admin_required
def remove_image(request):
    key = request.POST.get('key')
    try:
        image = Image.get(key)
        image.delete()
        return HttpResponse('deleted', mimetype='text/plain')
    except:
        raise Http404('Image not found')
