__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '20 April 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import logging
from django import forms
from django.conf import settings
from google.appengine.api import mail

# perart imports
from perart import models

class PerArtForm(forms.ModelForm):
    tinymce = True

class ProgramForm(PerArtForm):
    class Meta:
        model = models.Program
        exclude = ['url']


class ProjectForm(PerArtForm):
    class Meta:
        model = models.Project
        exclude = ['url']


class NewsForm(PerArtForm):
    class Meta:
        model = models.News
        exclude = ['url']


class MenuForm(PerArtForm):
    tinymce = False

    class Meta:
        model = models.Menu
        exclude = ['url']


class GalleryForm(PerArtForm):
    class Meta:
        model = models.Gallery
        exclude = ['url']


class NewsletterForm(forms.Form):
    name  = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    def send_email(self):
        try:
            mail.send_mail(sender='perart.office@gmail.com',
                           to=settings.PERART_EMAIL,
                           subject='"%(name)s" se prijavio za newsletter' % self.cleaned_data,
                           body='Ime: %(name)s\nEmail: %(email)s' % self.cleaned_data)
            return True
        except:
            logging.exception('sending message failed')
            return False
    