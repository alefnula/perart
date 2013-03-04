__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '16 May 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from tea.gae.decorators import admin_required

from perart.models import Settings, Menu


@admin_required
def main_menu_edit(request):
    
    menu = Settings.get_object(Settings.MAIN_MENU)
    if request.method == 'POST':
        menu = request.POST.get('menu', '')
        try:
            Menu.create(menu, {})
        except Exception, error:
            return render_to_response('perart/admin/main_menu_edit.html', {'menu': menu, 'error': error, 'page': 'main_menu'}, 
                                      context_instance=RequestContext(request))
        Settings.set_object(Settings.MAIN_MENU, menu)
        return HttpResponseRedirect(reverse('perart.admin.settings.main_menu_edit') + '?saved=1')
    return render_to_response('perart/admin/main_menu_edit.html', {'menu': menu, 'page': 'main_menu'}, 
                              context_instance=RequestContext(request))



@admin_required
def main_page_edit(request):
    text = Settings.get_object(Settings.MAIN_PAGE)
    if request.method == 'POST':
        text = request.POST.get('text', '')
        Settings.set_object(Settings.MAIN_PAGE, text)
        return HttpResponseRedirect(reverse('perart.admin.settings.main_page_edit') + '?saved=1')
    return render_to_response('perart/admin/main_page_edit.html', {'text': text, 'page': 'main_page'}, 
                              context_instance=RequestContext(request))