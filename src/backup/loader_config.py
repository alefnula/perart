import base64
from google.appengine.tools import bulkloader

def from_string(s):
    return None if s is None else s.encode('utf-8')

def from_key(s):
    return None if s is None else from_string(str(s))

def from_bool(s):
    return s

def from_blob(s):
    return None if s is None else base64.b64encode(s)


class ProgramExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Program',
                                           [('title',   from_string, None),
                                           ('url',      from_string, None),
                                           ('subtitle', from_string, None),
                                           ('text',     from_string, None)])


class ImageExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Image',
                                           [('title',    from_string, None),
                                           ('program',   from_key,    None),
                                           ('project',   from_key,    None),
                                           ('frontpage', from_bool,   None),
                                           ('image',     from_blob,   None)])

exporters = [ProgramExporter, ImageExporter]