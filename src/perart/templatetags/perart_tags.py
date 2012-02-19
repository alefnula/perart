__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '07 May 2009'
__copyright__ = 'Copyright (c) 2009 Viktor Kerkez'

from django import template

register = template.Library()


@register.inclusion_tag('perart/templatetags/render_gallery.html')
def render_gallery(gallery):
    '''Render a complete gallery'''
    images = gallery.images
    return { 'images': images, 'count': len(images) }
