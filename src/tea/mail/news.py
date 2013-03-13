__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '27 November 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

'''
Simple and complete library for sending news
'''

__all__ = ['NNTPConnection', 'NewsMessage', 'NewsMultiAlternatives', 'send_news']

import os
import time
import socket
import random
import nntplib
import mimetypes
from email.Header import Header
from email import Charset, Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate, parseaddr, formataddr

from tea.logger import * #@UnusedWildImport
from tea.utils.html import strip_tags
from tea.utils.encoding import smart_unicode, smart_str

# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
Charset.add_charset('utf-8', Charset.SHORTEST, Charset.QP, 'utf-8')

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = 'application/octet-stream'

# Default charset
DEFAULT_CHARSET = 'utf-8'

# Cache the hostname, but do it lazily: socket.getfqdn() can take a couple of
# seconds, which slows down the restart of the server.
class CachedDnsName(object):
    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, '_fqdn'):
            self._fqdn = socket.getfqdn()
        return self._fqdn

DNS_NAME = CachedDnsName()

# Copied from Python standard library, with the following modifications:
# * Used cached hostname for performance.
# * Added try/except to support lack of getpid() in Jython (#5496).
def make_msgid(idstring=None, utc=False):
    '''Returns a string suitable for RFC 2822 compliant Message-ID, e.g:

    <20020201195627.33539.96671@nightshade.la.mastaler.com>

    Optional idstring if given is a string used to strengthen the
    uniqueness of the message id.
    '''
    if utc:
        timestamp = time.gmtime()
    else:
        timestamp = time.localtime()
    utcdate = time.strftime('%Y%m%d%H%M%S', timestamp)
    try:
        pid = os.getpid()
    except AttributeError:
        # No getpid() in Jython, for example.
        pid = 1
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    idhost = DNS_NAME
    msgid = '<%s.%s.%s%s@%s>' % (utcdate, pid, randint, idstring, idhost)
    return msgid



class BadHeaderError(ValueError):
    pass



def forbid_multi_line_headers(name, val):
    '''Forbids multi-line headers, to prevent header injection.'''
    val = smart_unicode(val)
    if '\n' in val or '\r' in val:
        raise BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (val, name))
    try:
        val = val.encode('ascii')
    except UnicodeEncodeError:
        if name.lower() in ('to', 'from', 'cc'):
            result = []
            for item in val.split(', '):
                nm, addr = parseaddr(item)
                nm = str(Header(nm, DEFAULT_CHARSET))
                result.append(formataddr((nm, str(addr))))
            val = ', '.join(result)
        else:
            val = Header(val, DEFAULT_CHARSET)
    else:
        if name.lower() == 'subject':
            val = Header(val)
    return name, val



class SafeMIMEText(MIMEText):
    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val)
        MIMEText.__setitem__(self, name, val)



class SafeMIMEMultipart(MIMEMultipart):
    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val)
        MIMEMultipart.__setitem__(self, name, val)



class NNTPConnection(object):
    '''A wrapper that manages the SMTP network connection.'''
    def __init__(self, host, port=None, username=None, password=None, fail_silently=False):
        self.host = host
        self.port = port or 119
        self.username = username
        self.password = password
        self.fail_silently = fail_silently
        self.connection = None

    def open(self):
        '''Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        '''
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.
            self.connection = nntplib.NNTP(self.host, self.port, self.username, self.password)
            return True
        except Exception, e:
            LOG_ERROR('Error trying to connect to server %s:%s: %s' % (self.host, self.port, e))
            if not self.fail_silently:
                raise

    def close(self):
        '''Closes the connection to the email server.'''
        try:
            try:
                self.connection.quit()
            except Exception, e:
                LOG_ERROR('Error trying to close connection to server %s:%s: %s' % (self.host, self.port, e))
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, messages):
        '''Sends one or more NewsMessage objects and returns the number of news
        messages sent.
        '''
        if not messages:
            return
        new_conn_created = self.open()
        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return
        num_sent = 0
        for message in messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        if new_conn_created:
            self.close()
        return num_sent

    def _send(self, message):
        '''A helper method that does the actual sending.
        
        This method replaces the post method of the connection.
        '''
        try:
            resp = self.connection.shortcmd('POST')
            # Raises error_??? if posting is not allowed
            if resp[0] != '3':
                raise nntplib.NNTPReplyError(resp)
            for line in message.message().as_string().splitlines():
                if line[:1] == '.':
                    line = '.' + line
                self.connection.putline(line)
            self.connection.putline('.')
            self.connection.getresp()
        except Exception, e:
            LOG_ERROR('Error sending a message to server %s:%s: %s' % (self.host, self.port, e))
            if not self.fail_silently:
                raise
            return False
        return True



class NewsMessage(object):
    '''A container for news information.'''
    content_subtype = 'plain'
    multipart_subtype = 'mixed'
    encoding = None     # None => use settings default

    def __init__(self, subject='', body='', sender=None, newsgroups=None,
                 attachments=None, headers=None, connection=None):
        '''Initialize a single news message.

        All strings used to create the message can be unicode strings (or UTF-8
        bytestrings). The SafeMIMEText class will handle any necessary encoding
        conversions.
        '''
        assert not isinstance(newsgroups, basestring), '"newsgroups" argument must be a nonempty list or tuple'
        assert list(newsgroups) != [], '"newsgroups" argument must be a nonempty list or tuple'
        self.newsgroups = list(newsgroups)
        self.sender = sender
        self.subject = subject
        self.body = body
        self.attachments = []
        for attachment in (attachments or []):
            if isinstance(attachment, (tuple, list)):
                self.attach(*attachment)
            else:
                self.attach(attachment)
        self.extra_headers = headers or {}
        self.connection = connection

    def get_connection(self, fail_silently=False):
        if not self.connection:
            self.connection = NNTPConnection(fail_silently=fail_silently)
        return self.connection

    def message(self):
        encoding = self.encoding or DEFAULT_CHARSET
        msg = SafeMIMEText(smart_str(self.body, DEFAULT_CHARSET), self.content_subtype, encoding)
        if self.attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.multipart_subtype)
            if self.body:
                msg.attach(body_msg)
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))
        msg['Subject']    = self.subject
        msg['From']       = self.sender
        msg['Newsgroups'] = ', '.join(self.newsgroups)
        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = make_msgid()
        for name, value in self.extra_headers.items():
            msg[name] = value
        return msg

    def send(self, fail_silently=False):
        '''Sends the email message.'''
        return self.get_connection(fail_silently).send_messages([self])

    def attach(self, filename=None, content=None, mimetype=None):
        '''Attaches a file with the given filename and content. The filename can
        be omitted (useful for multipart/alternative messages) and the mimetype
        is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        '''
        if isinstance(filename, MIMEBase):
            assert content == mimetype == None
            self.attachments.append(filename)
        elif content is None and os.path.isfile(filename):
            self.attach_file(filename, mimetype)
        else:
            assert content is not None
            self.attachments.append((filename, content, mimetype))

    def attach_file(self, path, mimetype=None):
        '''Attaches a file from the filesystem.'''
        filename = os.path.basename(path)
        content = open(path, 'rb').read()
        self.attach(filename, content, mimetype)

    def _create_attachment(self, filename, content, mimetype=None):
        '''Converts the filename, content, mimetype triple into a MIME attachment
        object.
        '''
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            attachment = SafeMIMEText(smart_str(content, DEFAULT_CHARSET), subtype, DEFAULT_CHARSET)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            Encoders.encode_base64(attachment)
        if filename:
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        return attachment



class NewsMultiAlternatives(NewsMessage):
    '''A version of NewsMessage that makes it easy to send multipart/alternative
    messages. For example, including text and HTML versions of the text is
    made easier.
    '''
    multipart_subtype = 'alternative'

    def attach_alternative(self, content, mimetype=None):
        '''Attach an alternative content representation.'''
        self.attach(content=content, mimetype=mimetype)



def send_news(subject, sender, newsgroups, message=None, html_message=None, attachments=None,
              host='localhost', port=None, auth_user=None, auth_password=None, fail_silently=False):
    '''Easy wrapper for sending a single message to a newsgroup list.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the NewsMessage class directly.
    '''
    if message is None and html_message is None:
        raise ValueError('Either message or html_message must be provided')
    if message is None:
        message = strip_tags(html_message)
    connection = NNTPConnection(host=host, port=port, username=auth_user,
                                password=auth_password, fail_silently=fail_silently)
    # Convert the to field just for easier usage
    if isinstance(newsgroups, basestring):
        newsgroups = [newsgroups]
    if html_message is None:
        news = NewsMessage(subject=subject, body=message, sender=sender, newsgroups=newsgroups,
                           attachments=attachments, connection=connection)
    else:
        news = NewsMultiAlternatives(subject=subject, body=message, sender=sender, newsgroups=newsgroups,
                                     attachments=attachments, connection=connection)
        news.attach_alternative(html_message, 'text/html')
    return news.send()
