__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'


import time
import threading
from tea.logger import * #@UnusedWildImport


class AbstractCallback(object):
    '''Abstract callback class for the worker.
    
    These are the methods that needs to be implemented:
    '''        
    def start(self, title='', is_progress=False):
        pass
    
    def update(self, progress):
        pass
    
    def finish(self, succeeded, message):
        pass
    
    def __str__(self):
        return self.__class__.__name__


class Synchronizer(object):
    def __init__(self):
        self.result = False
        self.event = threading.Event()
    
    def finish(self, result):
        self.result = result
        self.event.set()

    def wait(self):
        self.event.wait()   


class Worker(threading.Thread):
    def __init__(self, callback=None):
        threading.Thread.__init__(self)
        self.callback = callback
        self.succeeded = False
        self.really_finished_lock = threading.Lock()
        
    def start(self):
        LOG_DEBUG('%s.start - Acquiring Lock' % self)
        self.really_finished_lock.acquire()
        threading.Thread.start(self)
    
    def wait(self):
        threading.Thread.join(self)
        # Now wait for all additional action to happen 
        while self.really_finished_lock.locked():
            time.sleep(0.1)
    
    def emit_start(self, title='', is_progress=False):
        if self.callback is not None:
            self.callback.start(title, is_progress)
    
    def emit_update(self, progress):
        if self.callback is not None:
            self.callback.update(progress)
    
    def emit_finish(self, succeeded=True, message=''):
        self.succeeded = succeeded
        try:
            if self.callback is not None:
                self.callback.finish(succeeded, message)
        finally:
            self.really_finished_lock.release()
            
    def emit_question(self, message, synchronizer):
        if self.callback is not None:
            self.callback.question(message, synchronizer)
        

    def __str__(self):
        return self.__class__.__name__
