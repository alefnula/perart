__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from google.appengine.api import users

def cms_data(request):
    return {
        'logout_url'       : users.create_logout_url('/'),
        'removed'          : True if request.REQUEST.get('removed') else False,
        'updated'          : True if request.REQUEST.get('updated') else False,
        'saved'            : request.REQUEST.get('saved', False), 
    }
