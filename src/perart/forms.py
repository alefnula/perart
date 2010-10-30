__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '20 April 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import models
from django import forms
from google.appengine.ext.db import djangoforms


class ProgramForm(djangoforms.ModelForm):
    frontpage_imagefield = forms.FileField(label='Frontpage Image', required=False)
    page_imagefield      = forms.FileField(label='Page Image', required=False)
    class Meta:
        model = models.Program
        exclude = ['url', 'frontpage_image', 'page_image', 'menu']


class ProjectForm(djangoforms.ModelForm):
    class Meta:
        model = models.Project
        exclude = ['url']


class NewsForm(djangoforms.ModelForm):
    class Meta:
        model = models.News
        exclude = ['url']


class GalleryForm(djangoforms.ModelForm):
    class Meta:
        model = models.Gallery
        exclude = ['url']
