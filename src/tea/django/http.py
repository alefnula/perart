__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '07 May 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.core.serializers import json, serialize

class JsonResponse(HttpResponse):
    def __init__(self, object, status=200):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(object, indent=2, cls=json.DjangoJSONEncoder, ensure_ascii=False)
        if settings.DEBUG:
            super(JsonResponse, self).__init__(content, content_type='text/plain', status=status)
        else:
            super(JsonResponse, self).__init__(content, content_type='application/json', status=status)
