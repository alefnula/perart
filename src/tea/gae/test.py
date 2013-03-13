__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import os

# Setup needed for GAE
os.environ['SERVER_NAME'] = 'localhost'
os.environ['SERVER_PORT'] = '8000'


def login():
    os.environ['USER_EMAIL']    = 'test@example.com'
    os.environ['USER_IS_ADMIN'] = '0'

def login_as_admin():
    os.environ['USER_EMAIL']    = 'test@example.com'
    os.environ['USER_IS_ADMIN'] = '1'
    
def logout():
    if 'USER_EMAIL' in os.environ:
        del os.environ['USER_EMAIL']
    if 'USER_IS_ADMIN' in os.environ:
        del os.environ['USER_IS_ADMIN']
