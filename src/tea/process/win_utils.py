__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '19 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import os
import sys
import wmi
import shlex
import pythoncom
from tea.logger import * #@UnusedWildImport
from win_process import ShellProcess


def execute(command, *args):
    '''Execute a command with arguments and wait for output.
    Arguments should not be quoted!
    
    >>> print 'status: %s, output: %s, error: %s' % execute('python', '-c', 'import sys;sys.stdout.write("out");sys.stderr.write("err");sys.exit(1)')
    status: 1, output: out, error: err
    '''
    process = ShellProcess(command, args)
    process.start()
    process.wait()
    return (process.exit_code, process.read(), process.eread())


def execute_and_report(command, *args):
    '''Executes a command with arguments and wait for output.
    If execution was successful function will return True,
    if not, it will log the output using standard logging and return False.
    '''
    LOG_INFO('Execute: %s %s' % (command, ' '.join(args)))
    status = -1
    out    = ''
    err    = ''
    try:
        status, out, err = execute(command, *args)
    except:
        LOG_EXCEPTION('%s failed! Exception thrown!' % os.path.basename(command))
        return False
    if status == 0:
        LOG_INFO('%s Finished successfully. Exit Code: 0.' % os.path.basename(command))
        return True
    else:
        try:
            LOG_ERROR('%s failed! Exit Code: %s\nOut: %s\nError: %s' % (os.path.basename(command), status, out, err))
        except:
            # This fails when some non ASCII characters are returned from the application
            LOG_ERROR('%s failed! Exit Code: %s\nOut: %s\nError: %s' % (os.path.basename(command), status, repr(out), repr(err)))            
        return False


def execute_nowait(command, *args):
    '''Execute a command with arguments and doesn't wait for output.
    Arguments should not be quoted!
    
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait('python', '-c', 'import sys;sys.stdout.write("out");sys.stderr.write("err");sys.exit(1)')
    status: None, output: out, error: err
    '''
    process = ShellProcess(command, args, redirect_output=False)
    process.start()
    return process


def execute_free(command, *args):
    '''Execute a command with arguments and wait for output.
    Arguments can be in a free form!
    
    >>> print 'status: %s, output: %s, error: %s' % execute_free('python', '-c', '"import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(1)"')
    status: 1, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_free('python', '-c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(2)"')
    status: 2, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_free('python -c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(3)"')
    status: 3, output: out, error: err
    '''
    arguments = command
    for arg in args:
        arguments += ' %s' % arg
    arguments = shlex.split(arguments)
    return execute(*arguments)


def execute_nowait_free(command, *args):
    '''Execute a command with arguments and doesn't wait for output.
    Arguments can be in a free form!
    
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('python', '-c', '"import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(1)"')
    status: None, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('python', '-c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(2)"')
    status: None, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('python -c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(3)"')
    status: None, output: out, error: err
    '''
    arguments = command
    for arg in args:
        arguments += ' %s' % arg
    arguments = shlex.split(arguments)
    return execute_nowait(*arguments)


def get_processes(sort_by_name=True):
    '''Retreaves a list of processes sorted by name.
    
    @type  sort_by_name: boolean
    @param sort_by_name: Sort the list by name or by pid
    @rtype:  list[tuple(string, int)]
    @return: List of process name, proces pid tuples
    '''
    
    '''if 'win' in sys.platform:
        win32pdh.EnumObjects(None, None, win32pdh.PERF_DETAIL_WIZARD)
        junk, instances = win32pdh.EnumObjectItems(None,None,'Process', win32pdh.PERF_DETAIL_WIZARD)
    
        proc_dict = {}
        for instance in instances:
            if proc_dict.has_key(instance):
                proc_dict[instance] = proc_dict[instance] + 1
            else:
                proc_dict[instance] = 1
    
        
        for instance, max_instances in proc_dict.items():
            for inum in xrange(max_instances):
                hq = win32pdh.OpenQuery() # initializes the query handle 
                try:
                    path = win32pdh.MakeCounterPath( (None, 'Process', instance, None, inum, 'ID Process') )
                    counter_handle = win32pdh.AddCounter(hq, path) #convert counter path to counter handle
                    try:
                        win32pdh.CollectQueryData(hq) #collects data for the counter 
                        type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
                        processes.append((instance, val))
                    except win32pdh.error, e:
                        LOG_EXCEPTION('Error retreaving process list')
                    win32pdh.RemoveCounter(counter_handle)
                except win32pdh.error, e:
                    LOG_EXCEPTION('Error retreaving process list')
                win32pdh.CloseQuery(hq)
    '''
    processes = []
    if 'win' in sys.platform:
        pythoncom.CoInitialize() #@UndefinedVariable
        try:
            c = wmi.WMI(find_classes=False)
            for i in c.Win32_Process(['ProcessID', 'Caption']):
                processes.append((i.ProcessID, i.Caption))
        finally:
            pythoncom.CoUninitialize() #@UndefinedVariable
    if sort_by_name:
        return sorted(processes, lambda t1, t2: cmp(t1[1], t2[1]) or cmp(t1[0], t2[0]))
    else:
        return sorted(processes, lambda t1, t2: cmp(t1[0], t2[0]) or cmp(t1[1], t2[1]))


def get_processes_with_cmdline(sort_by_name=True):
    processes = []
    if 'win' in sys.platform:
        pythoncom.CoInitialize() #@UndefinedVariable
        try:
            c = wmi.WMI(find_classes=False)
            for i in c.Win32_Process(['ProcessID', 'Caption', 'CommandLine']):
                processes.append((i.ProcessID, i.Caption, i.CommandLine))
        finally:
            pythoncom.CoUninitialize() #@UndefinedVariable
    if sort_by_name:
        return sorted(processes, lambda t1, t2: cmp(t1[1], t2[1]) or cmp(t1[0], t2[0]))
    else:
        return sorted(processes, lambda t1, t2: cmp(t1[0], t2[0]) or cmp(t1[1], t2[1]))


def find_process(name):
    '''Find process by name'''
    for id, process in get_processes():
        if process.lower().find(name.lower()) != -1:
            return process, id
    return None


def find_script(executable, script):
    '''Find process by name in command lines'''
    for id, process, cmdline in get_processes_with_cmdline():
        if process.lower().find(executable.lower()) != -1:
            if cmdline is not None and cmdline.lower().find(script.lower()) != -1:
                return process, id
    return None


def kill_process(process):
    '''Kills a process started by subprocess module
    '''
    if 'win' in sys.platform:
        # TODO: Proveriti return value i ako je False - GetLastError
        #win32process.TerminateProcess(int(process._handle), -1)
        execute(os.path.join(os.environ['windir'], 'system32', 'taskkill.exe'), '/PID', str(process.pid), '/F', '/T')
        #ctypes.windll.kernel32.TerminateProcess(int(process._handle), -1)
    else:
        pass


def kill_pid(pid):
    '''Kills a process by process PID
    '''
    if 'win' in sys.platform:
        #PROCESS_TERMINATE = 1
        #handle = win32api.OpenProcess(PROCESS_TERMINATE, False, pid)
        #win32api.TerminateProcess(handle, -1)
        #win32api.CloseHandle(handle)
        execute(os.path.join(os.environ['windir'], 'system32', 'taskkill.exe'), '/PID', str(pid), '/F', '/T')
    else:
        pass
