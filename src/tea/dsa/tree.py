__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import types


class Tree(object):
    def __init__(self, data=None):
        self.parent   = None
        self.data     = data
        self.forest   = []
    
    def __repr__(self):
        return 'Tree[data=%s]' % self.data
    __str__ = __repr__
    
    def add(self, tree):
        self.forest.append(tree)
        tree.parent = self
    
    def at(self, index):
        try:
            return self.forest[index]
        except IndexError:
            return None
    
    def index_of(self, tree):
        try:
            return self.forest.index(tree)
        except ValueError:
            return -1
    
    def __len__(self):
        return len(self.forest)

    def depth_first(self):
        yield self
        for tree in self.forest:
            for item in tree.depth_first():
                yield item
        
    def breadth_first(self):
        queue = [self]
        while len(queue) > 0:
            tree = queue.pop(0)
            queue.extend(tree.forest)
            yield tree



class TableTree(Tree):
    def __init__(self, data=None):
        Tree.__init__(self, data)

    def at_row(self, index):
        return self.at(index)

    def row_of(self, tree):
        return self.index_of(tree)

    def row_count(self):
        return len(self)
    
    def column_count(self):
        if type(self.data) in (types.ListType, types.TupleType):
            return len(self.data)
        return 1

    def at_column(self, column=None):
        if column is None:
            return self.data
        else:
            try:
                return self.data[column]
            except IndexError:
                return None

    def row(self):
        if self.parent is not None:
            return self.parent.row_of(self)
        return 0
