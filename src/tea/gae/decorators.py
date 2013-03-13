__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import functools
from google.appengine.api import users
from django.http import HttpResponseRedirect


def admin_required(function):
    '''Extension to Django's login_required decorator.
    
    Allows only application administrator to see the current view.
    The login redirect URL is always set to request.path
    '''
    @functools.wraps(function)
    def admin_required_wrapper(request, *args, **kw):
        if users.is_current_user_admin():
            return function(request, *args, **kw)
        return HttpResponseRedirect(users.create_login_url(request.path))
    return admin_required_wrapper
