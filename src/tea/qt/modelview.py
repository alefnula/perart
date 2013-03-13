__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from tea.logger import *


class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent, headers_func):
        super(Model, self).__init__(parent)
        self.headers_func = headers_func
        self.columns = 0
        self.root = self.get_items()
        self.headers = self.headers_func()

    def refresh(self):
        try:
            self.root = self.get_items()
            self.reset()
        except:
            LOG_EXCEPTION('Model.refresh() failed!')

    def get_items(self):
        raise NotImplementedError    
    
    def rowCount(self, index):
        return self.node_from_index(index).row_count()

    def columnCount(self, index):
        return self.node_from_index(index).column_count()

    def data(self, index, role):  
        if role == Qt.TextAlignmentRole:
            return QtCore.QVariant(int(Qt.AlignVCenter|Qt.AlignLeft))
        elif role == Qt.SizeHintRole:
            size = QtCore.QSize()
            size.setHeight(20)
            return QtCore.QVariant(size)
        elif role == Qt.DisplayRole:
            node = self.node_from_index(index)
            assert node is not None
            return QtCore.QVariant(node.at_column(index.column()))
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return QtCore.QVariant(self.headers[section])
        else:
            return QtCore.QVariant()

    def index(self, row, column, parent):
        assert self.root
        branch = self.node_from_index(parent)
        assert branch is not None
        return self.createIndex(row, column, branch.at_row(row))

    def parent(self, child):
        node = self.node_from_index(child)
        if node is None:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent is None:
            return QtCore.QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QtCore.QModelIndex()
        row = grandparent.row_of(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def node_from_index(self, index):
        return index.internalPointer() if index.isValid() else self.root
            
    def update_headers(self):
        self.headers = self.headers_func()

    def get_row_count(self):
        return self.root.row_count()




class TableView(QtGui.QTableView):
    def __init__(self, parent=None, selection_mode=QtGui.QAbstractItemView.SingleSelection):
        super(TableView, self).__init__(parent)
        # Setup sorted model
        self.model = None
        self.sorted_model = QtGui.QSortFilterProxyModel(self)
        self.setModel(self.sorted_model)
        # Setup table interface
        self.setSortingEnabled(True)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(selection_mode)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.setShowGrid(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setAlternatingRowColors(True)

    def set_model(self, model):
        self.model = model
        self.sorted_model.setSourceModel(self.model)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange and self.model is not None:
            self.model.update_headers()
        else:
            QtGui.QTableView.changeEvent(self, event)
        
    def refresh(self):
        self.model.refresh()   

#    def show_column(self, index):
#        self.horizontalHeader().showSection(index)
#
#    def hide_column(self, index):
#        self.horizontalHeader().hideSection(index)


class TreeView(QtGui.QTreeView):
    def __init__(self, parent=None, selection_mode=QtGui.QAbstractItemView.SingleSelection):
        super(TreeView, self).__init__(parent)
        # Setup sorted model
        self.model = None
        self.sorted_model = QtGui.QSortFilterProxyModel(self)
        self.setModel(self.sorted_model)
        # Setup table interface
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(selection_mode)
        self.header().setMovable(False)
        self.header().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setUniformRowHeights(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setAlternatingRowColors(True)

    def set_model(self, model):
        self.model = model
        self.sorted_model.setSourceModel(self.model)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange and self.model is not None:
            self.model.update_headers()
        else:
            QtGui.QTreeView.changeEvent(self, event)

    def refresh(self):        
        self.model.refresh()
