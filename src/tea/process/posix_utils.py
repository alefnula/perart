__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '19 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import os
import shlex
import posix #@UnresolvedImport
import signal
from tea.logger import * #@UnusedWildImport
from posix_process import ShellProcess


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
    '''Retrieves a list of processes sorted by name.
    
    @type  sort_by_name: boolean
    @param sort_by_name: Sort the list by name or by PID
    @rtype:  list[tuple(string, string)]
    @return: List of process PID, process name tuples
    '''
    command = ['ps', 'h', '-eo', 'pid,comm']
    status, out, error = execute(*command) #@UnusedVariable
    processes = []
    if status == 0:
        for line in out.splitlines():
            pid, name = line.strip().split(' ', 1)
            # FIXME: int moze da pukne!
            processes.append((int(pid), name))
    if sort_by_name:
        return sorted(processes, lambda t1, t2: cmp(t1[1], t2[1]) or cmp(int(t1[0]), int(t2[0])))
    else:
        return sorted(processes, lambda t1, t2: cmp(int(t1[0]), int(t2[0])) or cmp(t1[1], t2[1]))


def get_processes_with_cmdline(sort_by_name=True):
    '''Retreaves a list of processes sorted by name.
    
    @type  sort_by_name: boolean
    @param sort_by_name: Sort the list by name or by pid
    @rtype:  list[tuple(string, string, string)]
    @return: List of (process_pid, proces_name, proces_commandline) tuples
    '''
    command = ['ps', 'h', '-eo', 'pid,comm,args']
    status, out, error = execute(*command) #@UnusedVariable
    processes = []
    if status == 0:
        for line in out.splitlines():
            parts = line.strip().split(' ', 3)
            # TODO: Int moze da pukne
            processes.append((int(parts[0]), parts[1], ' '.join(parts[2:]).strip()))
    if sort_by_name:
        return sorted(processes, lambda t1, t2: cmp(t1[1], t2[1]) or cmp(t1[0], t2[0]))
    else:
        return sorted(processes, lambda t1, t2: cmp(t1[0], t2[0]) or cmp(t1[1], t2[1]))


def find_process(name):
    '''Find process by name'''
    for id, process in get_processes():
        # FIXME: HACK!!! Daje samo prvih 15 karaktera!!!
        if process.lower().find(name[:15].lower()) != -1 and '<defunct>' not in process.lower():
            return process, id
    return None


def find_script(executable, script):
    '''Find process by name in command lines'''
    for id, process, cmdline in get_processes_with_cmdline():
        # FIXME: HACK!!! Daje samo prvih 15 karaktera!!!
        if process.lower().find(executable[:15].lower()) != -1:
            if cmdline is not None and cmdline.lower().find(script.lower()) != -1:
                return process, id
    return None


def kill_process(process):
    '''Kills a process started by subprocess module
    '''
    if process.pid == posix.getpgid(process.pid):
        os.killpg(process.pid, signal.SIGKILL) #@UndefinedVariable
    else:
        os.kill(process.pid, signal.SIGKILL) #@UndefinedVariable
    

def kill_pid(pid):
    '''Kills a process by process PID.

    @type pid: int
    @param pid: Process ID of the process to kill 
    '''
    if pid == posix.getpgid(pid):
        os.killpg(pid, signal.SIGKILL) #@UndefinedVariable
    else:
        os.kill(pid, signal.SIGKILL) #@UndefinedVariable
