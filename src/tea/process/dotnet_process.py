__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '19 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import os
import re
import sys
import threading
from System.Diagnostics import Process #@UnresolvedImport


class ShellProcess(object):
    def __init__(self, command, arguments=None, environment=None, redirect_output=True):
        self._process  = Process()
        self._process.StartInfo.FileName, self._process.StartInfo.Arguments = self._get_cmd(command, [] if arguments is None else arguments)
        # FIXME: Kako ovo da podesimo?!?!? 
        #self._process.StartInfo.EnvironmentVariables = environment
        self._redirect_output = redirect_output
        self._process.StartInfo.UseShellExecute = False
        self._process.StartInfo.RedirectStandardInput  = redirect_output
        self._process.StartInfo.RedirectStandardOutput = redirect_output
        self._process.StartInfo.RedirectStandardError  = redirect_output
        self._stdout = ''
        self._stdout_lock = threading.Lock()
        self._stderr = ''
        self._stderr_lock = threading.Lock()
        self._reader_thread = None

    def _get_cmd(self, command, arguments):
        if command.endswith('.py'):
            arguments = [command] + list(arguments)
            command = os.path.join(sys.prefix, 'ipy.exe')
        elif command.endswith('.pyw'):
            arguments = [command] + list(arguments)
            command = os.path.join(sys.prefix, 'ipyw.exe')
        args = []
        for argument in arguments:
            if re.search(r'\s', argument):
                args.append(r'"%s"' % argument)
            else:
                args.append(argument)
        arguments = ' '.join(args)
        return command, arguments

    def _reader(self):
        while self.is_running():
            with self._stdout_lock:
                self._stdout += self._process.StandardOutput.ReadToEnd()
            with self._stderr_lock:
                self._stderr += self._process.StandardError.ReadToEnd()
        # Final read after process has finished
        with self._stdout_lock:
            self._stdout += self._process.StandardOutput.ReadToEnd()
        with self._stderr_lock:
            self._stderr += self._process.StandardError.ReadToEnd()

    def start(self):
        self._process.Start()
        if self._redirect_output:
            self._reader_thread = threading.Thread(target=self._reader)
            self._reader_thread.start()

    def kill(self):
        self._process.Kill()

    def wait(self, timeout=None):
        if timeout is not None:
            return self._process.WaitForExit(timeout)
        else:
            self._process.WaitForExit()
            return True

    def is_running(self):
        return not self._process.HasExited
        
    def _get_pid(self):
        return self._process.Id
   
    def _get_exit_code(self):
        if self._process.HasExited:
            return self._process.ExitCode
        return None

    def write(self, string):
        if self._redirect_output:
            self._process.StandardInput.WriteLine(string)
    
    def read(self):
        if self._redirect_output:
            with self._stdout_lock:
                result = self._stdout
                self._stdout = ''
            return result
        return ''
    
    def eread(self):
        if self._redirect_output:
            with self._stderr_lock:
                result = self._stderr
                self._stderr = ''
            return result
        return ''
    
    pid       = property(_get_pid)
    exit_code = property(_get_exit_code)
