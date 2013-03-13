__author__    = 'Viktor Kerkez <viktor.kerkez@gmail.com>'
__date__      = '18 December 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import os
import pickle
import base64
from StringIO import StringIO
try:
    from xml.etree import ElementTree as ET #@UnusedImport
except:
    from elementtree import ElementTree as ET #@Reimport @UnresolvedImport



FUNCTIONS = '''
import base64
import pickle

def get(name):
    data_struct = pickle.loads(base64.b64decode(DATA_STRUCT))
    start, end = data_struct.get(name, (0, 0))
    if start == end:
        return ''
    return base64.b64decode(DATA[start:end])

def list():
    data_struct = pickle.loads(base64.b64decode(DATA_STRUCT))
    return data_struct.keys()
'''


class RCC(object):
    '''Resource compiler class'''
    @classmethod
    def _write_data(cls, f, name, data):
        f.write('%s = \'\'\'\\' % name)
        while True:
            line = data.read(80)
            if line == '':
                f.write('\n\'\'\'\n\n')
                return
            f.write('\n' + line + '\\')
    
    @classmethod
    def compile(cls, resource, output):
        resource = os.path.abspath(resource)
        output = os.path.abspath(output)
        root = os.path.dirname(resource) 
        xml = ET.parse(resource)
        data_struct = {}
        data = StringIO()
        for resource in xml.findall('resource'):
            prefix = resource.get('prefix')
            for file in resource.findall('file'):
                start = data.len
                data.write(base64.b64encode(open(os.path.join(root, file.text), 'rb').read()))
                end = data.len
                if prefix != '':
                    path = '%s/%s' % (prefix.strip('/'), file.get('alias').strip('/'))
                else:
                    path = file.get('alias')
                data_struct[path] = (start, end)
        f = open(output, 'wb')
        data.seek(0)
        RCC._write_data(f, 'DATA', data)
        RCC._write_data(f, 'DATA_STRUCT', StringIO(base64.b64encode(pickle.dumps(data_struct))))
        f.write(FUNCTIONS)
        f.close()
        return 0
