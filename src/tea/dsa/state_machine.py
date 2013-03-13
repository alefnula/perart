__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '18 February 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import time
import threading
from Queue import Queue
from tea.logger import * #@UnusedWildImport


class StateMachineException(Exception):
    def __init__(self, message='', state='UNKNOWN'):
        self.message = message
        self.state = state

    def __repr__(self):
        return 'StateMachineException: %s , in state=%s' % (self.message, self.state)
    
    __str__ = __repr__



class State(object):
    '''State is the base class of all states that L{StateMachine} can be found
    in.
    
    State class is a wrapper for the "real" representation of the state.
    The "real" state which must be provided to the __init__ method.
    
    State class have four significant methods: L{on_event}, L{on_success},
    L{on_failure}, L{get_transit_state}.
    
    B{ALL OF THEM MUST BE OVERRIDEN IN EVERY SUBCLASS!!!}
    '''
    def __init__(self, state):
        '''Initialization
        
        @type  state: object.
        @param state: Represents the "real" L{StateMachine} state 
        '''
        self.state = state
    
    def on_event(self, event):
        '''This method B{must} be overridden by every subclass of the State class.
        
        In this method State object will call the appropriate
        B{in_state_<state>_action} method of the event, handle errors and
        returns True or False depending on the success of the event execution.
        
        @type  event: L{Event}
        @param event: Event to execute.
        @rtype:  boolean
        @return: True if event execution was successful, False otherwise
        ''' 
        raise NotImplementedError('State.on_event')

    def on_success(self, event):
        '''This method B{must} be overridden by every subclass of the State class.
        
        In this method State object will call the appropriate
        B{in_state_<state>_succeeded} method of the event and return the state
        in which the L{StateMachine} should go on successful event execution.
        
        @type  event: L{Event}
        @param event: Event to query for new state.
        @rtype:  object
        @return: New state of the of the L{StateMachine}.
        ''' 
        raise NotImplementedError('State.on_success')
    
    def on_failure(self, event):
        '''This method *must* be overridden by every subclass of the State class.
        
        In this method State object will call the appropriate
        B{in_state_<state>_failed} method of the event and return the state
        in which the L{StateMachine} should go on unsuccessful event execution.
        
        @type  event: L{Event}
        @param event: Event to query for new state.
        @rtype:  object
        @return: New state of the of the StateMachine.
        ''' 
        raise NotImplementedError('State.on_failure')
    
    def get_transit_state(self, event):
        '''This method *must* be overridden by every subclass of the State class.
        
        In this method State object will call the appropriate
        B{in_state_<state>_transit} method of the event and return the state
        in which the L{StateMachine} should be during the event execution.
        
        @type  event: L{Event}
        @param event: Event to query for new state.
        @rtype:  object
        @return: New state of the of the StateMachine.
        ''' 
        raise NotImplementedError('State.get_transit_state')

    def __repr__(self):
        return self.__class__.__name__
    
    __str__ = __repr__



class Event(object):
    '''Event is the base class of all events that can be executed in the
    L{StateMachine}.
    
    Every event should implement:
        - B{in_state_<STATE>_action} - Performs event action. This function
            B{must} return B{True} or B{False} to indicate the success or
            failure of event execution. It can also throw an exception. If the
            method throws an exception, exception will be propagated outside
            of the state machine.
        - B{in_state_<STATE>_succeeded} - Returns the new state in which the
            L{StateMachine} will go if the event was successfully executed.
        - B{in_state_<STATE>_failed} - Returns the new state in which the
            L{StateMachine} will go if the execution of the event failed.
        - B{in_state_<STATE>_transit} - Returns the state in which the
            L{StateMachine} will be during the event execution.
    For every state in which the event can be executed.
    
    Default behavior of the event is to raise L{NotImplementedError} for every
    B{in_state_<STATE>_*} method that is not implemented but gets called.
    
    If the event must return a result, this result should be stored in the
    L{result} variable of the Event. This result will be return on synchronous
    calls from the L{StateMachineCaller}. 
    '''
    def __init__(self):
        '''Initialization'''
        self.executor = None
        self.result = None

    def set_executor(self, executor):
        '''This method is called by StateMachine before event execution.

        L{StateMachine} will set itself as the executor of the event. During
        the execution of the event L{StateMachine} instance will be available
        to the Event via the L{executor} variable.
        '''
        self.executor = executor

    def __getattr__(self, attribute):
        '''This method is used to create a default implementation for all
        methods which names start with B{in_state_}. The default implementation
        will throw L{NotImplementedError} instead of L{AttributeError} which is
        thrown when the method is not found.
        
        This is used to help debug programs because of the frequent use of the
        B{in_state_} methods inside the L{StateMachine}.
        '''
        if attribute.startswith('in_state_'):
            raise NotImplementedError('%s.%s not implemented!' % (self, attribute)) 
        else:
            raise AttributeError('"%s" object has no attribute "%s"' % (self.__class__.__name__, attribute))

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__



class StateMachine(object):
    '''This is the actual implementation of the state machine, but should never
    be used because it is not thread safe. Instead user application should
    always use the L{StateMachineCaller} class which implements thread safety,
    and ensures that only one event is executed at the time.
    
    The theory behind the state machine is simple: StateMachine class has a
    state and executes events. After the event is executed machine changes it
    state according the the events request.
    
    Also the blank StateMachine class not useful. You should always subclass it
    add custom states and then use it. The pattern of subclassing should be:
    
    (You must always implement the required methods for the state class.
    But for demonstration reasons they will be excluded here.)
    
    >>> class MyFirstState(State): pass
    >>> class MySecondState(State): pass
    >>> class MyThirdState(State): pass
    
    >>> class MyStateMachine(StateMachine):
    ...     def __init__(self):
    ...         StateMachine.__init__(self, MyFirstState())
    ...         self._add_state(MySecondState())
    ...         self._add_state(MyThirdState())
    '''
    def __init__(self, startup_state_object):
        '''Initialization
        
        @type  startup_state_object: L{State}
        @param startup_state_object: State in which the StateMachine will be
            when it's initialized. Initial state must be supplied during the
            initialization of the state machine.
            States can be also added later. Usually in the __init__ method
            itself.        
        '''
        self._states = {}
        self._state_object = startup_state_object
        self._add_state(startup_state_object)
        # Setting and getting _current_event must be synchronized because
        # someone can query the state of the machine, and machine (if
        # _current_event exists) will return the transit state, but in between
        # on_event can set the _current_event to None, which will produce error
        self._current_event = None
        self._current_event_lock = threading.Lock()
   
    def _add_state(self, state_object):
        '''Adds a State to StateMachine.
        
        States in which the StateMachine can be are added by its subclasses
        in the __init__ method using this function.
        
        @type  state_object: L{State}
        @param state_object: State which needs to be added to the StateMachine
        '''
        self._states[state_object.state] = state_object
   
    def _add_states(self, state_objects):
        '''Adds a States to StateMachine.
        
        States in which the StateMachine can be are added by the subclasses
        in the __init__ method using this function.
        @type  state_objects: tuple(L{State}, L{State}, ...)
        @param state_objects: States which need to be added to the StateMachine
        '''
        for state_object in state_objects:
            self._add_state(state_object)
   
    def on_event(self, event):
        '''Execution of an event
        
        B{All events must be executed sequentially, error can occur if more
        than one event is executed in parallel.}
        
        StateMachine will first set the event as the current_event, after that
        it will set itself as the executor of the event (via L{Event.set_executor}),
        and in the end it will pass the event to it's current state_object for
        execution.
        After execution StateMachine will change its state according to the
        return value of the on_success/on_failure methods depending on the
        result of the event execution.
        
        @type  event: L{Event}
        @param event: Event to be executed. 
        '''
        LOG_DEBUG('%s.on_event(event=%s) - Started' % (self, event))
        self._current_event_lock.acquire()
        self._current_event = event
        self._current_event_lock.release()
        event.set_executor(self)
        try:
            LOG_INFO('%s - Executing' % event)
            succeeded = self._state_object.on_event(event)
            # README: If the result None it is assumed it is True
            if succeeded is None: succeeded = True
            LOG_INFO('%s - Execution finished, succeeded=%s' % (event, succeeded))
        except Exception, e:
            LOG_ERROR('%s - Execution failed (exception %s occurred)' % (event, e))
            self._current_event_lock.acquire()
            self._current_event = None
            self._current_event_lock.release()
            raise
        # README: If the event programmer forgot to return True/False, None
        #         will be retrieved. None is considered to represent successful
        #         execution.
        # TODO: Sredi ovde da logovanje bude lepse
        if succeeded:
            new_state = self._state_object.on_success(event)
        else:
            new_state = self._state_object.on_failure(event)
        LOG_DEBUG('%s - Changing state from=%s to=%s' % (event, self.state, new_state))
        if self._state_object.state != new_state:
            LOG_INFO('%s [%s -> %s]' % (self, self._state_object.state, new_state))
            if new_state not in self._states:
                self._current_event_lock.acquire()
                self._current_event = None
                self._current_event_lock.release()
                raise StateMachineException('StateMachine tried to switch into unknown state', str(new_state))
            self._state_object = self._states[new_state]
        self._current_event_lock.acquire()
        self._current_event = None
        self._current_event_lock.release()
        LOG_DEBUG('%s.on_event(event=%s) - Finished' % (self, event))

    def _get_state(self):
        '''Return the current state of the StateMachine
        
        If an event is handled during the call to this method, the transit state
        retrieved from the event is returned. Otherwise the current state object
        is queried for the state. 
        '''
        self._current_event_lock.acquire()
        if self._current_event is not None:
            state = self._state_object.get_transit_state(self._current_event)
        else:
            state = self._state_object.state
        self._current_event_lock.release()
        return state
    state = property(_get_state)

    def __repr__(self):
        return self.__class__.__name__
    __str__ = __repr__


# TODO: Docstring lepse opisi
class CallerEvent(object):
    '''CallerEvent object is used to wrap the L{Event} objects and fill the
    L{StateMachineCaller} event queue. Depending on the attributes of the
    CallerEvent, L{Event} is executed synchronously or asynchronously.
    
    CallerEvent must be provided with an L{Event} (sm_event) or
    L{threading.Event} (can_work) object, B{but not both}.
    If B{sm_event} is provided, the event will be executed when it comes in
    order.
    If B{can_work} is provided, the event will be I{set} when object is I{get}
    from the queue. After that the event loop will call I{wait()} on the
    finished event and wait for the I{sync_event} to execute the event.
    '''
    def __init__(self, sm_event=None, can_work=None):
        '''Initialization
        
        @type  sm_event: L{Event}
        @param sm_event: StateMachine event
        @type  can_work: L{threading.Event}
        @param can_work: Event that indicates the caller that it can proceed
            with the event execution.
        '''    
        if sm_event is None and can_work is None:
            raise StateMachineException('CallerEvent did not received neither sm_event nor can_work')
        if sm_event is not None and can_work is not None:
            raise StateMachineException('CallerEvent received both sm_event=%s and can_work=%s' % (sm_event, can_work))
        self.sm_event = sm_event
        self.can_work = can_work
        # finished is used only when can_work is provided
        if can_work is not None:
            self.finished = threading.Event()



class DeferredEvent(threading.Thread):
    '''DeferedEvent object returned when a *defer_method* is called on the
    L{StateMachineCaller}.
    
    The only purpose of the object is to place the event in the StateMachine
    queue after the timeout is exceeded, although this can be prevented by
    calling L{cancel} before the timeout is exceeded.
    '''
    def __init__(self, sm_caller, event, timeout):
        threading.Thread.__init__(self)
        self.sm_caller = sm_caller
        self.event = event
        self.timeout = timeout
        self.canceled = threading.Event()
        self.start()

    def run(self):
        start_time = time.time()
        while (time.time() - start_time) < self.timeout and not self.canceled.isSet():
            time.sleep(1)
        if not self.canceled.isSet():
            self.sm_caller.async_event(self.event)
    
    def cancel(self):
        '''Cancel the event execution'''
        self.canceled.set()
        
    def __repr__(self):
        return 'DefferedEvent <%s>' % self.event
    
    __str__ = __repr__



class StateMachineCaller(threading.Thread):
    '''StateMachineCaller is used for controlling the StateMachine in
    multithreaded environment.
    
    StateMachineCaller ensures that only one event is executed at a time
    (synchronizes the StateMachine object), manages an event queue and provides
    synchronous and asynchronous execution of events.
    '''
    def __init__(self, state_machine):
        '''Initialization
        
        Initialize the caller thread, since the StateMachineCaller is a thread,
        creates the StateMachine and event queue objects and starts the thread.
        
        @type  state_machine: L{StateMachine}
        @param state_machine: Controlled StateMachine
        '''
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self.state_machine = state_machine
        self.event_queue = Queue()
        self.setDaemon(True)
        self.start()

    def get_current_state(self):
        '''Returns the current state of the controlled StateMachine
        '''
        return self.state_machine.state
        
    def async_event(self, event):
        '''Asynchronous event execution

        Event will be put in the queue and executed when it gets in order.
        '''
        LOG_DEBUG('%s.async_event(event=%s)' % (self, event))
        self.event_queue.put(CallerEvent(sm_event=event))

    def sync_event(self, event):
        '''Synchronous event execution

        Method will wait until the event gets in order for execution, and then
        it will execute the event.
        '''
        LOG_DEBUG('%s.sync_event(event=%s)' % (self, event))
        can_work = threading.Event()
        queue_event = CallerEvent(can_work=can_work)
        try:
            self.event_queue.put(queue_event)
            can_work.wait()
            LOG_DEBUG('%s.sync_event(event=%s) - executing' % (self, event))
            self.state_machine.on_event(event)
        finally:
            queue_event.finished.set()

    def defer_event(self, event, timeout):
        '''Defer an event execution
        
        Method returns a L{DefferedEvent} object which will put the event in the
        state machine event queue after the timeout is exceeded.
        L{DeferredEvent} object has a *cancel* method which will, if it is called
        before the event is put into the queue, cancel the event.
        ''' 
        return DeferredEvent(self, event, timeout)

    def start(self):
        LOG_INFO('Starting %s' % self)
        self._stopevent.clear()
        threading.Thread.start(self)
    
    def stop(self):
        LOG_INFO('Stopping %s' % self)
        self._stopevent.set()
    
    def run(self):
        '''Thread main loop
        
        Gets events from the event_queue and, depending on the event type
        (synchronous or asynchronous), executes the event or informs the caller
        that the event is ready for execution and waits for the caller to finish
        the event execution.
        '''
        while not self._stopevent.isSet():
            queue_item = self.event_queue.get()
            if queue_item.sm_event is not None:
                LOG_DEBUG('%s.run - Async event found in queue, event=%s' % (self, queue_item.sm_event))
                try:
                    self.state_machine.on_event(queue_item.sm_event)
                except Exception, e:
                    LOG_ERROR('%s.run - Error while running event=%s! Exception: %s' % (self, queue_item.sm_event, e))
            else:
                LOG_DEBUG('%s.run - Sync event found in queue' % self)
                queue_item.can_work.set()
                queue_item.finished.wait()

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__



class SubEvent(Event):
    '''SubEvent is used to carry the event to the I{SubMachine} of the 
    L{StateMachineWithSubMachine}.
    
    SubEvent will receive the I{SubMachine} L{Event} in __init__.
    When SubEvent is executed it should (in appropriate state) call:
    L{_send_event_to_submachine} which will propagate this call to the to
    executors I{SubMachine} (executor is the L{StateMachine} which executes the
    event).
    '''
    def __init__(self, subevent):
        '''Initialization
        
        @type  subevent: L{Event}
        @param subevent: SubMachine Event
        '''
        Event.__init__(self)
        self.subevent = subevent

    def _send_event_to_submachine(self):
        '''Sends objects L{subevent} to appropriate SubMachine of the
        executor, which is in this case a L{StateMachineWithSubMachine}.

        This method should be called from the appropriate I{in_state_<STATE>}
        method of the event.
        ''' 
        self.executor.send_event_to_submachine(self.subevent)



class StateMachineWithSubMachine(StateMachine):
    '''Implementation of the two leveled L{StateMachine}.
    
    This StateMachine has a SubMachine. SubMachine will receive an event when
    the event type is SubEvent. SubEvent will call L{send_event_to_submachine}
    on the executor i.e. StateMachineWithSubMachine and this method will
    propagate the event to the SubMachine.
    '''
    def __init__(self, startup_state_object, submachine=None):
        '''Initialization
        
        Setup the StateMachine and set the SubMachine, if the SubMachine is
        provided during the initialization. SubMachine can be later assigned
        to object variable L{submachine}.
        '''
        StateMachine.__init__(self, startup_state_object)
        self.submachine = submachine
    
    def _get_substate(self):
        '''Returns the state of the SubMachine'''
        return self.submachine.state
    substate = property(_get_substate)

    def send_event_to_submachine(self, event):
        '''Propagate the event to SubMachine'''
        self.submachine.on_event(event)



class StateMachineWithSubMachineCaller(StateMachineCaller):
    '''StateMachineWithSubMachineCaller adds just one functionality to the
    L{StateMachineCaller}, the method L{get_current_substate}
    ''' 
    def get_current_substate(self):
        '''Returns the current substate of the controlled L{StateMachine}, i.e.
        the state of the SubMachine.
        '''
        return self.state_machine.substate
