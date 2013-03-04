__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '20 April 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

# django imports
from django import forms
from django.core.mail import send_mail
from django.conf import settings

# perart imports
from perart import models

class ProgramForm(forms.ModelForm):
    class Meta:
        model = models.Program
        exclude = ['url', 'menu']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        exclude = ['url']


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.News
        exclude = ['url']


class GalleryForm(forms.ModelForm):
    class Meta:
        model = models.Gallery
        exclude = ['url']


class NewsletterForm(forms.Form):
    name  = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    def send_email(self):
        try:
            send_mail('"%(name)s" se prijavio za newsletter' % self.cleaned_data,
                      'Ime: %(name)s\nEmail: %(email)s' % self.cleaned_data,
                      'office@perart.org', settings.PERART_EMAIL, fail_silently=False)
            
            #settings.
            return True
        except:
            return False
    