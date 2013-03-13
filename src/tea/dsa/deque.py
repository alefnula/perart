__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import bisect
import threading
import collections
from tea.logger import * #@UnusedWildImport


class ComparatorProxy(object):
    def __init__(self, item, comparator):
        self.item = item
        self.comparator = comparator

    def __cmp__(self, other):
        if hasattr(self.item, self.comparator) and hasattr(other.item, other.comparator):
            return cmp(getattr(self.item, self.comparator), getattr(other.item, other.comparator))
        return 0

    def __str__(self):
        return str(self.item)
    
    def __repr__(self):
        return repr(self.item)



class Deque(object):
    '''This is an implementation of double ended queue.
    
    If a user provides an comparator it will also be a priority double ended queue
    '''
    def __init__(self, iterable=None, comparator=None):
        '''Build an ordered collection accessible from endpoints only'''
        self.__lock = threading.Lock() 
        if comparator is None:
            self.__priority_deque = False
            self.__comparator = None
            if iterable is None:
                self.__deque = collections.deque()
            else:
                self.__deque = collections.deque(iterable)
        else:
            self.__priority_deque = True
            self.__comparator = comparator
            self.__deque = []
            if iterable is not None:
                for item in iterable:
                    self.push_front(item)
    
    def __len__(self):
        with self.__lock:
            return len(self.__deque)
    
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, list(self.__deque))
    
    __str__ = __repr__
    
    def __add__(self, other):
        assert isinstance(other, Deque), 'Unsupported operand type(s) for +: "%s" and "%s"' % (
                                          self.__class__.__name__, other.__class__.__name__)
        assert self.__comparator == other.__comparator, 'Comparators does not match: %s and %s' % (
                                                         self.__comparator, other.__comparator)
        return Deque(list(self.__deque) + list(other.__deque))
    
    def __iter__(self):
        for item in self.__deque:
            if isinstance(item, ComparatorProxy):
                yield item.item
            else:
                yield item
    
    def extend_front(self, iterable):
        '''Extend the left side of the deque with elements from the iterable'''
        LOG_VERBOSE('Deque.extend_front(%s)' % iterable)
        with self.__lock:
            if self.__priority_deque:
                for item in iterable:
                    self.push_front(item)
            else:
                if isinstance(iterable, Deque):
                    self.__deque.extendleft(iterable.__deque)
                else:
                    self.__deque.extendleft(iterable)
    
    def extend_back(self, iterable):
        '''Extend the right side of the deque with elements from the iterable'''
        LOG_VERBOSE('Deque.extend_back(%s)' % iterable)
        with self.__lock:
            if self.__priority_deque:
                for item in iterable:
                    self.push_back(item)
            else:
                if isinstance(iterable, Deque):
                    self.__deque.extend(iterable.__deque)
                else:
                    self.__deque.extend(iterable)
    
    def push_front(self, item):
        '''Add an element to the left side of the Deque'''
        LOG_VERBOSE('Deque.push_front(%s)' % item)
        with self.__lock:
            if self.__priority_deque:
                bisect.insort_left(self.__deque, ComparatorProxy(item=item, comparator=self.__comparator))
            else:
                self.__deque.appendleft(item)
    
    def push_back(self, item):
        '''Add an element to the right side of the Deque'''
        LOG_VERBOSE('Deque.push_back(%s)' % item)
        with self.__lock:
            if self.__priority_deque:
                bisect.insort_right(self.__deque, ComparatorProxy(item=item, comparator=self.__comparator))
            else:
                self.__deque.append(item)
    
    def pop_front(self):
        '''Remove and return the leftmost element'''
        with self.__lock:
            if self.__priority_deque:
                item = self.__deque.pop(0).item
            else:
                item = self.__deque.popleft()
            LOG_VERBOSE('Deque.pop_front() -> %s' % item)
            return item
    
    def pop_back(self):
        '''Remove and return the rightmost element'''
        with self.__lock:
            if self.__priority_deque:
                item = self.__deque.pop().item
            else:
                item = self.__deque.pop()
            LOG_VERBOSE('Deque.pop_back() -> %s' % item)
            return item
        
    def back(self):
        '''Return the rightmost element, without removing it from Deque'''
        if self.__priority_deque:
            return self.__deque[-1].item
        else:
            return self.__deque[-1]
    
    def front(self):
        '''Return the leftmost element, without removing it from Deque'''
        if self.__priority_deque:
            return self.__deque[0].item
        else:
            return self.__deque[0]
    
    def empty(self):
        '''Is the Deque empty?'''
        LOG_VERBOSE('Deque.empty() - Current state: %s' % self.__deque)
        return len(self.__deque) == 0

    def clear(self):
        '''Remove all elements from the Deque'''
        LOG_VERBOSE('Deque.clear()')
        with self.__lock:
            if self.__priority_deque:
                self.__deque = []
            else:
                self.__deque.clear()

    def remove(self, item):
        '''Remove the item from Deque by specifying the item'''
        LOG_VERBOSE('Deque.remove(item=%s)' % item)
        with self.__lock:
            if self.__priority_deque:
                for i in range(len(self.__deque)):
                    if self.__deque[i].item == item:
                        del self.__deque[i]
                        break
            else:
                self.__deque.remove(item)
 
    def remove_by_index(self, index):
        '''Remove the item from Deque by specifying the index of the item in Deque'''
        with self.__lock:
            if self.__priority_deque:
                del self.__deque[index]
            else:
                self.__deque.remove(self.__deque[index])
 

__doc__ = '''
>>> # Normal Deque Tests
>>> d = Deque([1, 2, 3])
>>> d.front()
1
>>> d.pop_front()
1
>>> d.pop_front()
2
>>> d.push_front(4)
>>> d.pop_back()
3
>>> d.pop_back()
4
>>> d.empty()
True
>>> d.push_back(1)
>>> d.push_back(2)
>>> d.pop_back()
2
>>> d.clear()
>>> d.empty()
True
>>> # Priority Deque Tests
>>> class MyClass(object):
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...     def __repr__(self):
...         return 'MyClass(x=%s, y=%s)' % (self.x, self.y)
...     __str__ = __repr__
...
>>> d = Deque(comparator='x')
>>> d.push_front(MyClass(33, 44))
>>> d.push_front(MyClass(33, 55))
>>> d.push_back(MyClass(33, 22))
>>> d.push_back(MyClass(22, 11))
>>> d.push_front(MyClass(44, 11))
>>> print d
Deque([MyClass(x=22, y=11), MyClass(x=33, y=55), MyClass(x=33, y=44), MyClass(x=33, y=22), MyClass(x=44, y=11)])
>>> print d.pop_front()
MyClass(x=22, y=11)
>>> print d.pop_front()
MyClass(x=33, y=55)
>>> print d.pop_back()
MyClass(x=44, y=11)
>>> d.remove_by_index(1)
>>> print d
Deque([MyClass(x=33, y=44)])
>>> d.empty()
False
>>> item = d.front()
>>> d.remove(item)
>>> d.empty()
True
'''

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
