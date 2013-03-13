__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '27 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import tea

if tea.PLATFORM == tea.POSIX:
    from posix_process import *
    from posix_utils import *
elif tea.PLATFORM == tea.WINDOWS:
    from win_process import *
    from win_utils import *
elif tea.PLATFORM == tea.DOTNET:
    from dotnet_process import *
    from dotnet_utils import *
else:
    raise tea.PlatformError(tea.PLATFORM, 'process module is not supported!')
