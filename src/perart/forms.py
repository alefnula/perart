__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '20 April 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

# django imports
from django import forms

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
