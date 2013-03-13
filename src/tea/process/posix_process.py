__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '19 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import os
import time
import signal
import tempfile
import threading
import subprocess
from tea.logger import * #@UnusedWildImport


class ShellProcess(object):
    def __init__(self, command, arguments=None, environment=None, redirect_output=True):
        self._commandline = self._get_cmd(command, [] if arguments is None else arguments)
        # will be created on start
        self._environment     = environment
        self._process         = None
        self._wait_thread     = None
        self._redirect_output = redirect_output
        self._stdout_named    = None
        self._stderr_named    = None
        self._stdout_reader   = None
        self._stderr_reader   = None

    def _get_cmd(self, command, args):
        '''Internal helper function for merging command with arguments'''
        arguments = []
        if command.endswith('.py'):
            arguments = ['python', command] + list(args)
        else:
            arguments = [command] + list(args)
        return arguments

    def start(self):
        if self._redirect_output:
            self._stdout_named    = tempfile.NamedTemporaryFile()
            self._stderr_named    = tempfile.NamedTemporaryFile()
            self._stdout_reader   = open(self._stdout_named.name, 'rb') 
            self._stderr_reader   = open(self._stderr_named.name, 'rb')
            self._process = subprocess.Popen(self._commandline,
                                             stdin=subprocess.PIPE,
                                             stdout=self._stdout_named.file,
                                             stderr=self._stderr_named.file,
                                             env=self._environment)
        else:
            self._process = subprocess.Popen(self._commandline,
                                             stdin=None,
                                             stdout=open(os.devnull, 'wb'),
                                             stderr=subprocess.STDOUT,
                                             env=self._environment)
        self._wait_thread = threading.Thread(target=self._process.wait)
        self._wait_thread.setDaemon(True)
        self._wait_thread.start()

    def kill(self):
        try:
            os.kill(self._process.pid, signal.SIGKILL) #@UndefinedVariable
            # FIXME: Jel ovo treba posto vec imamo thread koji trci...?
            self._process.wait()
            return True
        except OSError:
            return False

    def wait(self, timeout=None):
        '''Wait for process to end'''
        if timeout is not None:
            current_time = time.time()
            while time.time() - current_time < timeout*1000:
                if not self._process.is_running():
                    return True
                time.sleep(0.1)
            return False
        else:
            while self.is_running():
                time.sleep(0.1)
            return True

    def is_running(self):
        if self._process is None or self._process.returncode is not None:
            return False
        return True

    def write(self, string):
        '''Send to stdin'''
        if self._redirect_output:
            if string[-1] != '\n':
                string = string + '\n'
            self._process.stdin.write(string)
            self._process.stdin.flush()

    def read(self):
        '''Get stdout'''
        if self._redirect_output:
            return self._stdout_reader.read()
        return ''

    def eread(self):
        '''Get stderr'''
        if self._redirect_output:
            return self._stderr_reader.read()
        return ''

    def _get_pid(self):
        return self._process.pid
   
    def _get_exit_code(self):
        if self.is_running():
            return None
        return self._process.returncode

    pid       = property(_get_pid)
    exit_code = property(_get_exit_code)
