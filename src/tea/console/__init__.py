__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '20 October 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'


import os
import re
import sys
import ctypes
from textwrap import TextWrapper

import tea
from tea.logger import LOG_ERROR


class Color(object):
    black  = 'black'
    blue   = 'blue'
    green  = 'green'
    cyan   = 'cyan'
    red    = 'red'
    purple = 'purple'
    yellow = 'yellow'
    gray   = 'gray'
    white  = 'white'
    normal = 'normal'
    
    @classmethod
    def colors(cls):
        return (cls.black,  cls.blue,   cls.green, cls.cyan,  cls.red,
                cls.purple, cls.yellow, cls.gray,  cls.white, cls.normal)
    
    @classmethod
    def color_re(cls):
        return re.compile(r'\[(?P<dark>dark\ )?(?P<color>%s)\]' % '|'.join(cls.colors()), re.MULTILINE)



if tea.PLATFORM in (tea.WINDOWS, tea.DOTNET):

    def _set_color(fg, bg, fg_dark, bg_dark, underlined):
        # System is Windows    
        STD_INPUT_HANDLE  = -10 #@UnusedVariable
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12 #@UnusedVariable
        # COLORS[fg or bg][is dark][color]
        COLORS = {
            'fg': {
                True:  {Color.black: 0x00, Color.blue:   0x01, Color.green:  0x02, Color.cyan:  0x03,
                        Color.red:   0x04, Color.purple: 0x05, Color.yellow: 0x06, Color.white: 0x07,
                        Color.gray:  0x08, Color.normal: 0x07},
                False: {Color.black: 0x00, Color.blue:   0x09, Color.green:  0x0A, Color.cyan:  0x0B,
                        Color.red:   0x0C, Color.purple: 0x0D, Color.yellow: 0x0E, Color.white: 0x0F,
                        Color.gray:  0x07, Color.normal: 0x07}
            },
            'bg': {
                True:  {Color.black: 0x00, Color.blue:   0x10, Color.green:  0x20, Color.cyan:  0x30,
                        Color.red:   0x40, Color.purple: 0x50, Color.yellow: 0x60, Color.white: 0x70,
                        Color.gray:  0x80, Color.normal: 0x00},
                False: {Color.black: 0x00, Color.blue:   0x90, Color.green:  0xA0, Color.cyan:  0xB0,
                        Color.red:   0xC0, Color.purple: 0xD0, Color.yellow: 0xE0, Color.white: 0xF0,
                        Color.gray:  0x70, Color.normal: 0x00}
            }
        }
        std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE) #@UndefinedVariable
        code = 0 | COLORS['fg'][fg_dark][fg] | COLORS['bg'][bg_dark][bg]
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, code) #@UndefinedVariable

elif tea.PLATFORM == tea.POSIX:

    def _set_color(fg, bg, fg_dark, bg_dark, underlined):       
        COLORS = {
            'fg': {
                Color.black: 30, Color.red:    31, Color.green: 32, Color.yellow: 33,
                Color.blue:  34, Color.purple: 35, Color.cyan:  36, Color.gray:   37,
                Color.white: 37, Color.normal: 00,
            },
            'bg': {
                Color.black: 40, Color.red:    41, Color.green: 42, Color.yellow: 43,
                Color.blue:  44, Color.purple: 45, Color.cyan:  46, Color.gray:   47,
                Color.white: 47, Color.normal: 00,
            }
        }
        args = set()
        if fg != Color.normal:
            if not fg_dark: args.add(1)
            args.add(COLORS['fg'][fg])
        if bg != Color.normal:
            args.add(COLORS['bg'][bg])
        if underlined:
            args.add(4)
        # White and gray are special cases
        if fg == Color.white:
            args.add(1)
        if fg == Color.gray:
            if fg_dark:
                args.update([1, 30])
                args.remove(37)
            else:
                args.remove(1)
        sys.stdout.write('\33[%sm' % ';'.join(map(str, args)))

else:
    LOG_ERROR('Color console is not supported!')

def set_color(fg=Color.normal, bg=Color.normal, fg_dark=False, bg_dark=False, underlined=False):
    '''Set the console color.
    
    >>> set_color(Color.red, Color.blue)
    >>> set_color('red', 'blue')
    >>> set_color() # returns back to normal
    '''
    _set_color(fg, bg, fg_dark, bg_dark, underlined)



def strip_colors(text):
    '''Helper function used to strip out the color tags so other function can
    determine the real text line lengths.
    
    @type  text: string
    @param text: Text to strip color tags from
    @rtype:  string
    @return: Stripped text.
    '''
    return Color.color_re().sub('', text)


def cprint(text, fg=Color.normal, bg=Color.normal, fg_dark=False, bg_dark=False, underlined=False, parse=False):
    '''Prints string in to stdout using colored font.
    
    See L{set_color} for more details about colors.
    
    @type  color: string or list[string]
    @param color: If color is a string than this is a color in which the text
        will appear. If color is a list of strings than all desired colors
        will be used as a mask (this is used when you wan to set foreground
        and background color).
    @type  text: string
    @param text: Text that needs to be printed. 
    '''
    if parse:
        color_re = Color.color_re()
        lines = text.splitlines()
        count = len(lines)
        for i, line in enumerate(lines):
            previous = 0
            end      = len(line)
            for match in color_re.finditer(line):
                sys.stdout.write(line[previous:match.start()])
                d = match.groupdict()
                set_color(d['color'], fg_dark=False if d['dark'] is None else True)
                previous = match.end()
            sys.stdout.write(line[previous:end] + ('\n' if i < count-1 or text[-1] == '\n' else ''))      
    else:
        set_color(fg, bg, fg_dark, bg_dark, underlined)
        sys.stdout.write(text)
        set_color()


def clear_screen(numlines=100):
    '''Clear the console.
    
    @type  numlines: integer
    @param numlines: This is an optional argument used only as a fall-back if
        the operating system console doesn't have clear screen function.
    @rtype: None
    '''
    if tea.PLATFORM == tea.POSIX:
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif tea.PLATFORM in (tea.WINDOWS, tea.WINDOWS_CE, tea.DOTNET):
        # DOS/Windows
        os.system('cls')
    else:
        # Fallback for other operating systems.
        print '\n' * numlines


def getch():
    '''Crossplatfrom getch() function.
    
    Same as the getch function from msvcrt library, but works on all platforms.
    @rtype:  string
    @return: One character got from standard input.
    '''
    if tea.PLATFORM == tea.POSIX:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    elif tea.PLATFORM == tea.MAC:
        import Carbon #@UnresolvedImport
        if Carbon.Evt.EventAvail(0x0008)[0] == 0: # 0x0008 is the keyDownMask
            return ''
        else:
            # The event contains the following info:
            # (what, msg, when, where, mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            what, msg, when, where, mod = Carbon.Evt.GetNextEvent(0x0008)[1] #@UnusedVariable
            return chr(msg & 0x000000FF)
    elif tea.PLATFORM in (tea.WINDOWS, tea.WINDOWS_CE, tea.DOTNET):
        msvcrt = ctypes.cdll.msvcrt
        return chr(msvcrt._getch())
    else:
        ch = raw_input()
        return (ch and ch[0]) or '\n'


def format_page(text):
    '''Formats the text for output adding ASCII frame around the text.
    
    @type  text: string
    @param text: Text that needs to be formated.
    @rtype:  string
    @return: Formated string.
    '''
    width = max(map(len, text.splitlines()))
    page = '+-' + '-'*width + '-+\n'
    for line in text.splitlines():
        page += '| ' + line.ljust(width) + ' |\n'
    page += '+-' + '-'*width + '-+\n'
    return page


def table(text):
    '''Formats the text as a table
    
    Text in format:
    
    first | second
    row 2 col 1 | 4
    
    Will be formated as
    +-------------+--------+
    | first       | second |
    +-------------+--------+
    | row 2 col 1 | 4      |
    +-------------+--------+

    @type  text: string
    @param text: Text that needs to be formated.
    @rtype:  string
    @return: Formated string.
    '''    
    table_bar = lambda col_lengths: '+-%s-+%s' % ('-+-'.join(map(lambda length: '-' * length, col_lengths)), os.linesep)
    rows  = []
    for line in text.splitlines():
        rows.append(map(string.strip, line.split('|')))
    max_cols = max(map(len, rows))
    col_lengths = [0] * max_cols
    for row in rows:
        cols = len(row)
        if cols < max_cols:
            row.extend([''] * (max_cols - cols))
        for i, col in enumerate(row):
            col_length = len(col)
            if col_length > col_lengths[i]:
                col_lengths[i] = col_length
    text = table_bar(col_lengths)
    for i, row in enumerate(rows):
        cols = []
        for i, col in enumerate(row):
            cols.append(col.ljust(col_lengths[i]))
        text += '| %s |%s' % (' | '.join(cols), os.linesep)
        text += table_bar(col_lengths)
    return text


def hbar(width):
    '''Returns ASCII HBar +---+ with the specified width.
    
    @type  width: integer
    @param width: Width of the central part of the bar.
    @rtype:  string
    @return: ASCII HBar.
    ''' 
    return '+-' + '-'*width + '-+'


def print_page(text):
    '''Formats the text and prints it on stdout.
    
    Text is formated by adding a ASCII frame around it and coloring the text.
    Colors can be added to text using color tags, for example:
        
        My [FG_BLUE]blue[NORMAL] text.
        My [BG_BLUE]blue background[NORMAL] text.
    
    
    '''
    color_re = re.compile(r'\[(?P<color>[FB]G_[A-Z_]+|NORMAL)\]')
    width = max(map(lambda x: len(strip_colors(x)), text.splitlines()))
    print '\n' + hbar(width)
    for line in text.splitlines():
        if line == '[HBAR]':
            print hbar(width)
            continue
        tail = width - len(strip_colors(line))
        sys.stdout.write('| ')
        previous = 0
        end      = len(line)
        for match in color_re.finditer(line):
            sys.stdout.write(line[previous:match.start()])
            set_color(match.groupdict()['color'])
            previous = match.end()
        sys.stdout.write(line[previous:end])
        sys.stdout.write(' '*tail + ' |\n')
    print hbar(width)


def wrap_text(text, width=80):
    '''Wraps text lines to maximum *width* characters.
    
    Wrapped text is aligned against the left text border.
    
    @type  text: string
    @param text: Text to wrap.
    @type  width: integer
    @param width: Maximum number of characters per line.
    @rtype:  string
    @return: Wrapped text.
    '''
    text = re.sub('\s+', ' ', text).strip()
    wrapper = TextWrapper(width=width, break_long_words=False,
                          replace_whitespace=True)
    return wrapper.fill(text)

    
def rjust_text(text, width=80, indent=0, subsequent=None):
    '''Same as L{wrap_text} with the difference that the text is aligned
    against the right text border.
    
    @type  text: string
    @param text: Text to wrap and align.
    @type  width: integer
    @param width: Maximum number of characters per line.
    @type  indent: integer
    @param indent: Indentation of the first line.
    @type  subsequent: integer or None
    @param subsequent: Indentation of all other lines, if it is None, then the
        indentation will be same as for the first line.
    '''
    text = re.sub('\s+', ' ', text).strip()
    if subsequent is None:
        subsequent = indent
    wrapper = TextWrapper(width=width, break_long_words=False,
                          replace_whitespace=True,
                          initial_indent=' '*(indent+subsequent),
                          subsequent_indent=' '*subsequent)
    return wrapper.fill(text)[subsequent:]


def center_text(text, width=80):
    '''Center all lines of the text.
    
    It is assumed that all lines width is smaller then B{width}, because the
    line width will not be checked.
    
    @type  text: string
    @param text: Text to wrap.
    @type  width: integer
    @param width: Maximum number of characters per line.
    @rtype:  string
    @return: Centered text.
    '''
    centered = []
    for line in text.splitlines():
        centered.append(line.center(width))
    return '\n'.join(centered)
