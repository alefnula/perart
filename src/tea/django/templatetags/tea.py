__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__date__      = '07 May 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

import re
from django import template
from django.conf import settings

register = template.Library()



ATTR_NUMERIC_TEST_RE = re.compile('^\d+$')

@register.filter
def attr(obj, a):
    '''Gets an attribute of an object dynamically from a string name.
    
    Usage: {{ object|getattr:dynamic_string_var }} 
    '''
    if hasattr(obj, str(a)):
        return getattr(obj, a)
    elif hasattr(obj, 'fields') and a in object.fields: # If object is a django form
        return obj[a]
    elif hasattr(obj, 'has_key') and obj.has_key(a):
        return obj[a]
    elif ATTR_NUMERIC_TEST_RE.match(str(a)) and len(obj) > int(a):
        return obj[int(a)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID



@register.filter
def classname(object):
    return object.__class__.__name__



@register.simple_tag
def model_name(form, plural=False):
    if plural:
        return form._meta.model._meta.verbose_name_plural
    return form._meta.model._meta.verbose_name



#
# Tea form generation tags
#

@register.inclusion_tag('tea/field.html')
def tea_field(field):
    return { 'field': field }


@register.inclusion_tag('tea/form.html')
def tea_form(form, submit_value=None):
    '''Create a form similar to one in django admin interface.'''
    return { 'form': form, 'submit_value': submit_value }



# JQuery function for generating TinyMCE editor from settings configuration

@register.inclusion_tag('tea/tinymce.html')
def tinymce():
    if hasattr(settings, 'TINY_MCE_SETTINGS'):
        TINY_MCE_SETTINGS = settings.TINY_MCE_SETTINGS
    else:
        TINY_MCE_SETTINGS = '''
script_url: '/static/js/tiny_mce/tiny_mce.js',
theme: 'advanced',
plugins: 'safari,emotions,preview,fullscreen',

theme_advanced_buttons1: 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,blockquote,|,link,unlink,|,forecolor,backcolor,|,hr,sub,sup,charmap,emotions',
theme_advanced_buttons2: 'undo,redo,|,formatselect,fontselect,fontsizeselect,|,fullscreen,code,preview,',
theme_advanced_buttons3: null,
theme_advanced_buttons4: null,
  
theme_advanced_toolbar_location: 'top',
theme_advanced_toolbar_align: 'left',
theme_advanced_statusbar_location: 'bottom',
theme_advanced_resizing: true,
relative_urls: false,
'''
    return {
        'TINY_MCE_SETTINGS': TINY_MCE_SETTINGS
    }
