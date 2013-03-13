__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '27 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import sys
import types
import traceback


def get_object(path='', object=None):
    if not path:
        return object
    if path.startswith('.'):
        if not object:
            raise TypeError('relative imports require the "object" argument')    
    path = path.split('.')
    if object is None:
        __import__(path[0])
        object = sys.modules[path[0]]
        path = path[1:]
    for item in path:
        if item != '':
            if type(object) == types.ModuleType:
                try:
                    __import__('%s.%s' % (object.__name__, item))
                except: pass
            object = getattr(object, item)
    return object


def get_exception():
    trace = ''
    exception = ''
    exc_list = traceback.format_exception_only(sys.exc_type, sys.exc_value) #@UndefinedVariable
    for entry in exc_list:
        exception += entry
    tb_list = traceback.format_tb(sys.exc_info()[2])
    for entry in tb_list:
        trace += entry    
    return '\n\n%s\n%s' % (exception, trace)
