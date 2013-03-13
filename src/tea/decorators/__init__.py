__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '28 December 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import time
import functools
from tea.logger import *

def trace(function):
    functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            LOG_EXCEPTION('tea.trace - %s' % function.__name__)
    return wrapper


def time_it(function):
    functools.wraps(function)
    def wrapper(*args, **kwargs):
        a = time.time()
        result = function(*args, **kwargs)
        b = time.time()
        LOG_INFO('Function: %s took %.4f seconds to run' % (function.__name__, b - a))
        return result
    return wrapper
