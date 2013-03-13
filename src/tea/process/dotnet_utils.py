__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '19 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import clr #@UnresolvedImport
clr.AddReference('System.Management')

import os
import shlex
from tea.logger import * #@UnusedWildImport
from dotnet_process import ShellProcess
from System.Diagnostics import Process #@UnresolvedImport
from System.Management import ManagementObjectSearcher #@UnresolvedImport


def execute(command, *args):
    '''Execute a command with arguments and wait for output.
    Arguments should not be quoted!
    
    >>> print 'status: %s, output: %s, error: %s' % execute('ipy', '-c', 'import sys;sys.stdout.write("out");sys.stderr.write("err");sys.exit(1)')
    status: 1, output: out, error: err
    '''
    #arguments = [command] + list(args)
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
    
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait('ipy', '-c', 'import sys;sys.stdout.write("out");sys.stderr.write("err");sys.exit(1)')
    status: None, output: out, error: err
    '''
    process = ShellProcess(command, args)
    process.start()
    return process


def execute_free(command, *args):
    '''Execute a command with arguments and wait for output.
    Arguments can be in a free form!
    
    >>> print 'status: %s, output: %s, error: %s' % execute_free('ipy', '-c', '"import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(1)"')
    status: 1, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_free('ipy', '-c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(2)"')
    status: 2, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_free('ipy -c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(3)"')
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
    
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('ipy', '-c', '"import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(1)"')
    status: None, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('ipy', '-c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(2)"')
    status: None, output: out, error: err
    >>> print 'status: %s, output: %s, error: %s' % execute_nowait_free('ipy -c "import sys;sys.stdout.write(\\'out\\');sys.stderr.write(\\'err\\');sys.exit(3)"')
    status: None, output: out, error: err
    '''
    arguments = command
    for arg in args:
        arguments += ' %s' % arg
    arguments = shlex.split(arguments)
    return execute_nowait(*arguments)


def get_processes(sort_by_name=True):
    '''Retrieves a list of processes sorted by name.
    
    @type  sort_by_name: boolean
    @param sort_by_name: Sort the list by name or by pid
    @rtype:  list[tuple(string, int)]
    @return: List of process name, process pid tuples
    '''
    processes = []
    searcher = ManagementObjectSearcher('select ProcessID, Caption from Win32_Process')    
    for process in searcher.Get():
        processes.append((int(process['ProcessID']), process['Caption']))
    if sort_by_name:
        return sorted(processes, lambda t1, t2: cmp(t1[1], t2[1]) or cmp(t1[0], t2[0]))
    else:
        return sorted(processes, lambda t1, t2: cmp(t1[0], t2[0]) or cmp(t1[1], t2[1]))


def get_processes_with_cmdline(sort_by_name=True):
    processes = []
    searcher = ManagementObjectSearcher('select ProcessID, Caption, CommandLine from Win32_Process')    
    for process in searcher.Get():
        processes.append((int(process['ProcessID']), process['Caption'], process['CommandLine'] or ''))
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
    process.kill()


def kill_pid(pid):
    '''Kills a process by process PID
    '''
    process = Process.GetProcessById(pid)
    process.Kill()
