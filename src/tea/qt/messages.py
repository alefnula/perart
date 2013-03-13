__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import inspect
from PyQt4 import QtGui, QtCore
from tea.utils import get_exception


def reformat_message(msg):
    '''Reformats the message:
    
     1. Gets the module name of the function that called the log function.
        - Get the stack.
        - Get the frame of the function that called the logging function.
        - Get the module name in which the frame was created.
    
    @type  msg: string
    @param msg: Log meessage.
    @rtype:  string
    @return: Reformated log message.
    '''
    # Get the stack:
    stack = inspect.stack()
    # Get the frame of the function that called the logging function:
    frame = stack[2][0]
    # Get the module in which the fram was created:
    module = inspect.getmodule(frame)
    # Get the module name:
    if module is None:
        module_name = '__main__'
    else:
        module_name = module.__name__
    return '[%s] - %s' % (module_name, msg)

SHOW_TRACE = True

def MSG_CONFIGURE(show_trace=True):
    global SHOW_TRACE
    SHOW_TRACE = show_trace


def MSG_INFO(msg, title=None, parent=None, reformat=False):
    title = title if title is not None else _('Information')
    if reformat: msg = reformat_message(msg)
    return QtGui.QMessageBox.information(parent, title, msg, QtGui.QMessageBox.Ok)


def MSG_WARNING(msg, title=None, parent=None, reformat=False):
    title = title if title is not None else _('Warning')
    if reformat: msg = reformat_message(msg)
    return QtGui.QMessageBox.warning(parent, title, msg, QtGui.QMessageBox.Ok)


def MSG_ERROR(msg, title=None, parent=None, reformat=False):
    title = title if title is not None else _('Error')
    if reformat: msg = reformat_message(msg)
    return QtGui.QMessageBox.critical(parent, title, msg, QtGui.QMessageBox.Ok)


def MSG_EXCEPTION(msg, title=None, parent=None, reformat=False):
    title = title if title is not None else _('Exception')
    if SHOW_TRACE: msg += get_exception()
    if reformat: msg = reformat_message(msg)
    return QtGui.QMessageBox.critical(parent, title, msg, QtGui.QMessageBox.Ok)


def MSG_YES_NO(question, title=None, default='yes', parent=None):
    title = title if title is not None else _('Question')
    if default.lower() == 'yes': default = QtGui.QMessageBox.Yes
    else: default = QtGui.QMessageBox.No
    result = QtGui.QMessageBox.question(parent, title, question,
                                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                        default)
    if result == QtGui.QMessageBox.Yes: return True
    else: return False

def MSG_OK_CANCEL(question, title=None, default='ok', parent=None):
    title = title if title is not None else _('Question')
    if default.lower() == 'ok': default = QtGui.QMessageBox.Ok
    else: default = QtGui.QMessageBox.Cancel
    result = QtGui.QMessageBox.question(parent, title, question,
                                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                        default)
    if result == QtGui.QMessageBox.Ok: return True
    else: return False


def MSG_INPUT(variable, title=None, default='', parent=None):
    title = title if title is not None else _('Input')
    name, f = QtGui.QInputDialog.getText(parent, QtCore.QString(variable),
                  QtCore.QString(title), QtGui.QLineEdit.Normal, QtCore.QString(default))
    if not f:
        return None
    return unicode(name).strip()
