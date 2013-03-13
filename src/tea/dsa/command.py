__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'


from threading import Lock
from tea.logger import * #@UnusedWildImport
from tea.dsa.deque import Deque


class IncorrectCommand(Exception):
    '''Exception thrown in case of errors inside the command_pattern classes.'''
    def __init__(self, command='', message='Failed to execute'):
        self.command = command
        self.message = message

    def __repr__(self):
        return 'Failed to execute: %s , %s' % (self.command, self.message)

    __str__ = __repr__



class NotUndoable(Exception):
    '''This exception is thrown when command cannot be reverted.
    
    Difference between L{NotUndoable} and L{CannotUndo} is that L{NotUndoable}
    is thrown when the command is generally not undoable by implementation
    (undo is not implemented) and L{CannotUndo} is thrown when an error
    occurred during the execution of the undo command.
    '''
    def __init__(self, command):
        self.command = command
        
    def __repr__(self):
        return '%s cannot be reverted!' % self.command
    
    __str__ = __repr__



class CannotUndo(Exception):
    '''This exception is thrown when command cannot be reverted.
    
    Difference between L{NotUndoable} and L{CannotUndo} is that L{NotUndoable}
    is thrown when the command is generally not undoable by implementation
    (undo is not implemented) and L{CannotUndo} is thrown when an error
    occurred during the execution of the undo command. 
    '''
    def __init__(self, command, reason):
        self.command = command
        self.reason = reason
        
    def __repr__(self):
        return '%s cannot be reverted, because: %s!' % (self.command, self.reason)
    
    __str__ = __repr__



class Command(object):
    '''Base class for all commands. Provides thread-safe command execute/execute_undo,
    exception logging and output logging. Command also takes care of sequence
    of calls - e.g. C{execute()} must be called before C{execute_undo()}.
    
    Basic usage is:
     1. Override L{do} and L{undo} methods to implement functionality.
     2. Call the new subclass by L{execute}, L{execute_undo}.
     3. Use C{self.output} and C{self.exceptions} to get results of execution.
    
    B{Method C{do} must be overridden to use this class.} C{undo} is optional, but
    preferred to be implemented as well.}
    
    @see: L{do}, L{undo}, L{execute}, L{execute_undo}
    '''
    
    def __init__(self):
        self.exception = None
        self.output    = None
        self.executed  = False
        self._lock     = Lock()

    def do(self):
        '''Override this method with code to be executed with L{execute}.
        B{I{do} method itself shouldn't be called directly.}
        
        @return: method output is saved in the B{output} variable of the
                Command instance.
        @see: L{execute}
        '''
        raise NotImplementedError()

    def undo(self):
        '''Override this method with code to be executed with L{execute_undo}.
        B{I{undo} method itself shouldn't be called directly.}
        
        @return: method output is saved in the B{output} variable of the
                Command instance.
        @see: L{is_undoable}, L{execute_undo}
        '''
        raise NotImplementedError()

    def execute(self):
        '''Executes the code in L{do} method.
        
        Method provides following:
          - thread-safe execution
          - output recording in C{self.output}
          - exceptions are saved in C{self.exceptions}
          - after execution enables L{execute_undo}
         
         @see: L{do}, L{execute_undo}
        '''
        self._lock.acquire()
        self.output = None
        self.exception = None
        try:
            LOG_INFO('Executing Command %s' % self)
            self.output = self.do()
            LOG_INFO('Executing Command %s succeeded' % self)
            return True
        except Exception, e:
            LOG_ERROR('Executing Command %s failed. Error: %s' % (self, e))
            self.exception = e
            return False
        finally:
            self.executed = True
            self._lock.release()
        
    def execute_undo(self):
        '''Executes the code in L{undo} method.
        
        Method provides following:
          - thread-safe execution
          - output recording in C{self.output}
          - exceptions are saved in C{self.exceptions}
          - after execution enables L{execute_undo}
         
         @see: L{undo}, L{execute}
        '''
        self._lock.acquire()
        self.output = None
        self.exception = None
        if not self.is_undoable():
            self._lock.release()
            raise NotUndoable(self)
        if not self.executed:
            self._lock.release()
            raise CannotUndo(self, 'Command not executed yet')
        try:
            self.output = self.undo()
            return True
        except Exception, e:
            self.exception = e
            return False
        finally:
            self.executed = False
            self._lock.release()
    
    def is_undoable(self):
        '''Checks if the undo() method has been overridden and returns
        the result.
        '''
        if self.__class__.undo.__hash__() == Command.undo.__hash__():
            return False
        return True
        
    def __repr__(self):
        return self.__class__.__name__
    
    __str__ = __repr__



class CommandQueue(object):
    '''Queue for sequential execution of L{commands <Command>}.
    '''
    UNDO_SAME    = 0
    UNDO_REVERSE = 1
    
    def __init__(self, commands=None, undo_direction=UNDO_REVERSE):
        '''Initialization
        
        @type  commands: iterable
        @param commands: List of the commands that needs to be executed.
            If commands are not provided, CommandQueue will be empty
            (Commands can be added later using L{add_command}
        @type  undo_direction: constant
        @param undo_direction: Direction of the undo commands.
            If the direction is:
                * L{CommandQueue.UNDO_SAME} - Commands will be executed in the
                    "undo" procedure in the same order they were executed in
                    the "do" procedure
                * L{CommandQueue.UNDO_REVERESE} - Commands will be executed in
                    the reverse order, i.e. the last command will be reverted
                    first.
            Default: L{CommandQueue.UNDO_REVERSE}
        '''
        if commands is not None:
            self._do_queue = Deque(iterable=commands, comparator='DO_PRIORITY')
        else:
            self._do_queue = Deque(comparator='DO_PRIORITY')
        self._undo_queue     = Deque(comparator='UNDO_PRIORITY')
        self._reverted_queue = Deque()
        self._undo_direction = undo_direction
        self._command        = None
        self._last_output    = None
        self._outputs        = []
        self._last_exception = None
        self._exceptions     = []
        self._lock           = Lock()

    def __repr__(self):
        return '<%s Do: [%s] Undo: [%s]>' % (self.__class__.__name__,
                                             ', '.join(map(repr, self._do_queue)),
                                             ', '.join(map(repr, self._undo_queue)))
    __str__ = __repr__

    def __len__(self):
        return len(self._do_queue)

    def __add__(self, other):
        return CommandQueue(self._do_queue + other._do_queue)

    def empty(self):
        return self._do_queue.empty()
    
    def empty_undo(self):
        return self._undo_queue.empty()

    def next(self):
        '''Executes the next command in queue.
        C{next} sets the C{self.output} and C{self.exceptions} with the data
        from the command executed.
        Method locks other queue manipulating methods during execution.
        
        @raise IndexError: if called on an empty queue 
        '''
        try:
            self._lock.acquire()
            self._last_output = None
            self._last_exception = None
            self._command = self._do_queue.pop_front()
            # Execute the command
            result = self._command.execute()
            # Get the output
            self._last_output = self._command.output
            self._outputs.append(self._command.output)
            # Check result and get the exception
            if result:
                return True
            else:
                self._last_exception = self._command.exception
                self._exceptions.append(self._command.exception)
                return False
        finally:
            self._undo_queue.push_back(self._command)
            self._lock.release()
    
    def _pop_next(self):
        '''DONT USE THIS METHOD!!!'''
        with self._lock:
            return self._do_queue.pop_front()
    
    def previous(self):
        '''Undoes the last executed command from queue.
        
        C{previous} sets the C{self.output} and C{self.exceptions} with the data
        from the command reverted.
        Method locks other queue manipulating methods during execution.
        
        @raise IndexError: if called before any command is executed 
        '''
        try:
            self._lock.acquire()
            self._last_output = None
            self._last_exception = None
            if self._undo_direction == CommandQueue.UNDO_SAME:
                self._command = self._undo_queue.pop_front()
            elif self._undo_direction == CommandQueue.UNDO_REVERSE:
                self._command = self._undo_queue.pop_back()
            else:
                raise CannotUndo(None, 'Unknown undo direction=%s!' % str(self._undo_direction))
            # Execute command undo
            result = self._command.execute_undo()
            # Get the output
            self._last_output = self._command.output
            self._outputs.append(self._command.output)
            # Check result and get the exception
            if result:
                return True
            else:
                self._last_exception = self._command.exception
                self._exceptions.append(self._command.exception)
                return False
        finally:
            self._reverted_queue.push_back(self._command)
            self._lock.release()

    def _pop_previous(self):
        '''DONT USE THIS METHOD!!!'''
        with self._lock:
            if self._undo_direction == CommandQueue.UNDO_SAME:
                return self._undo_queue.pop_front()
            elif self._undo_direction == CommandQueue.UNDO_REVERSE:
                return self._undo_queue.pop_back()

    def add_command(self, command):
        '''Adds a new command to the queue.
        
        Method locks other queue manipulating methods during execution.
        
        @type  command: L{Command}
        @param command: new command
        @raise IncorrectCommand: if passed command isn't a instance of L{Command}
        '''
        with self._lock:
            if not isinstance(command, Command):
                raise IncorrectCommand(command.__class__, 'Instance of Command must be provided!')
            self._do_queue.push_back(command)
    
    def remove_command(self, command):
        '''Removes a command from the queue, if it's not executed.
        
        Method locks other queue manipulating methods during execution.
        
        @param command: command to be removed
        @type command: L{Command}
        @raise ValueError: if passed command isn't in the queue
        '''
        with self._lock:
            self._do_queue.remove(command)
    
    def remove_command_by_index(self, command_index):
        '''Removes a command from the queue, if it's not executed.
        
        Method locks other queue manipulating methods during execution.
        
        @param command: index of the command to remove
        @type command: int
        @raise IndexError: if the index isn't in the queue
        '''
        with self._lock:
            self._do_queue.remove_by_index(command_index)
    
    def get_current_command(self):
        return self._command
    current_command = property(get_current_command)
    
    def get_output(self):
        return self._last_output
    output = property(get_output)
    
    def get_all_outputs(self):
        return self._outputs
    all_outputs = property(get_all_outputs)
    
    def get_exception(self):
        return self._last_exception
    exception = property(get_exception)

    def get_all_exceptions(self):
        return self._exceptions
    all_exceptions = property(get_all_exceptions)


#class FunctionCommand(Command):
#    '''Implements simple function execution without undo.
#    
#    Basic usage::
#        def reciever_method(param_name):
#            ...
#    
#        command = FunctionCommand(reciever_method, {'param_name': 'test value'})
#        command.execute()
#    '''
#    
#    def __init__(self, executable, params=None):
#        Command.__init__(self)
#        self.executable = executable
#        if params is None:
#            self.params = {}
#        else:
#            self.params = params
#
#    def do(self):
#        output = None
#        if callable(self.executable):
#            output = self.executable(**self.params)
#        else:
#            raise IncorrectCommand(self.__str__, 'not an executable')
#        return output
#    
#    def set_param(self, name, value):
#        self.params[name] = value
#        
#    def reset_params(self):
#        for key in self.params:
#            self.params[key] = None
#            
#    def __str__(self):
#        return self.executable.__name__
#
#
#
#class ClassCommand(FunctionCommand):
#    '''Implements simple class method execution without undo.
#    
#    Basic usage::
#        class Receiver():
#            def receiver_method(param):
#            ...
#    
#        command = ClassCommand(Receiver(), 'receiver_method', {'name': 122})
#        command.execute()
#    '''
#    def __init__(self, reciever, method_name, params=None):
#        FunctionCommand.__init__(self, getattr(reciever, method_name), params)
#        self.reciever = reciever
#        self.method_name = method_name
#    
#    def __str__(self):
#        return '%s.%s' % (self.reciever.__class__.__name__.split('.')[-1], self.method_name)
