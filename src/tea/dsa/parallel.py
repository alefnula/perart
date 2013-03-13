__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '20 October 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import time
import threading
from Queue import Queue
from tea.logger import * #@UnusedWildImport


class Thread(threading.Thread):
    def __init__(self, function, arguments):
        threading.Thread.__init__(self)
        self.function  = function
        self.arguments = arguments
        self.result    = None
        self.stats     = {
            'start_time' : 0,
            'end_time'   : 0,
        }

    def run(self):
        self.stats['start_time'] = time.time()
        try:
            if hasattr(self.arguments, '__iter__'):
                self.result = self.function(*self.arguments)
            else:
                self.result = self.function(self.arguments)
        except:
            LOG_EXCEPTION('Running function: %s failed' % self.function.__name__)
        self.stats['end_time'] = time.time()


class Pool(object):
    def __init__(self, pool_size=1000, sleep_time=0.1, stats=False):
        self._pool_size  = pool_size
        self._sleep_time = sleep_time
        self._stats      = stats
        self._waiting    = Queue()
        self._running    = Queue()
        self._finished   = Queue()
        self._semaphore  = threading.Semaphore(pool_size)


    def _start(self):
        self._filler_thread_finished = False
        self._filler_thread = threading.Thread(target=self._filler)
        self._filler_thread.start()
        self._emptier_thread = threading.Thread(target=self._emptier)
        self._emptier_thread.start()

    def _filler(self):
        while not self._waiting.empty():
            key, function, args = self._waiting.get()
            self._semaphore.acquire()
            thread = Thread(function, args)
            thread.start()
            self._running.put((key, thread))
        self._filler_thread_finished = True

    def _emptier(self):
        while True:
            key, thread = self._running.get()
            if thread.is_alive():
                self._running.put((key, thread))
            else:
                self._semaphore.release()
                if self._stats:
                    self._finished.put((key, thread.result, thread.stats))
                else:
                    self._finished.put((key, thread.result))
            if self._filler_thread_finished and self._running.empty():
                return
            time.sleep(self._sleep_time)

    def map(self, function, args_sequence, in_order=True): #@ReservedAssignment
        key_args_sequence = zip(xrange(len(args_sequence)), args_sequence)
        for result in self.key_map(function, key_args_sequence, in_order):
            if self._stats:
                yield result[1:]
            else:
                yield result[1]

    def key_map(self, function, key_args_sequence, in_order=True):
        for key, args in key_args_sequence:
            self._waiting.put((key, function, args))
        self._start()
        if in_order:
            finished = {}
            for key, _ in key_args_sequence:
                if key in finished:
                    yield finished[key]
                else:
                    result = self._finished.get()
                    while key != result[0]:
                        finished[result[0]] = result
                        result = self._finished.get()
                    yield result
        else:
            for _ in xrange(len(key_args_sequence)):
                yield self._finished.get()



if __name__ == '__main__':
    from dms_common.decorators import time_it

    def mapper(x):
        time.sleep(0.1)
        return x
    
    @time_it
    def test1():
        pool = Pool()
        print list(pool.map(mapper, range(30), True))

    @time_it
    def test2():
        pool = Pool()
        print list(pool.map(mapper, range(30), False))

    @time_it
    def test3():
        print map(mapper, range(30))

    test1()
    test2()
    test3()
