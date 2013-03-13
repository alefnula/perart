__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '27 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import sys
_names = sys.builtin_module_names

POSIX, MAC, WINDOWS, WINDOWS_CE, DOTNET, OS2, RISCOS,  = range(7)

PLATFORM_NAMES = {
    POSIX      : 'POSIX',
    MAC        : 'MAC',
    WINDOWS    : 'Windows NT',
    WINDOWS_CE : 'Windows CE',
    DOTNET     : '.NET',
    OS2        : 'OS2',
    RISCOS     : 'RISC OS'
}

class PlatformError(Exception):
    def __init__(self, platform, message):
        self.platform = platform
        self.message  = message
    
    def __repr__(self):
        return 'PlatformError [%s]: %s' % (PLATFORM_NAMES[self.platform], self.message)
    __str__ = __repr__


if 'clr' in _names:
    PLATFORM = DOTNET
elif 'posix' in _names:
    PLATFORM = POSIX
elif 'nt' in _names:
    PLATFORM = WINDOWS
elif 'os2' in _names:
    PLATFORM = OS2
elif 'mac' in _names:
    PLATFORM = MAC
elif 'ce' in _names:
    PLATFORM = WINDOWS_CE
elif 'riscos' in _names:
    PLATFORM = RISCOS
