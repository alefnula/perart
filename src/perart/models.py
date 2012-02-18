__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

import re
import string
import logging

from google.appengine.ext import db
from google.appengine.api import memcache, images

from django.db import models

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from djangotoolbox.fields import BlobField

# Constant for fetching all objects from db
FETCH_ALL = 1000



class PerartModel(object):
    def key(self):
        return self.id
    
    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def get_model_edit_url(cls):
        return reverse('perart.admin_%s_edit' % cls.name().lower())
    def get_object_edit_url(self):
        return reverse('perart.admin_%s_edit' % self.name().lower(), args=[self.key()])
    @classmethod
    def get_list_url(cls):
        return reverse('perart.admin_%s_list' % cls.name().lower())



class PerartModelWithTitleAndUrl(PerartModel):
    def __unicode__(self):
        return self.title    

    @classmethod
    def get_by_url(cls, url):
        object = memcache.get('%s-%s' % (cls.name(), url)) #@UndefinedVariable
        if object is None:
            object = cls.gql('WHERE url = :1', url).get()
            if object:
                memcache.set('%s-%s' % (cls.name(), url), object) #@UndefinedVariable
        return object

    @classmethod
    def get_unique_url(cls, url):
        '''Function takes in an url and checks if it's already used.
        
        If the url already exists then adds a number to the end of the url.
        '''
        url = unicode(slugify(url))
        nr = 0
        object = cls.get_by_url(url)
        while object:
            nr += 1
            url = '%s-%s' % (url, nr)
            object = cls.get_by_url(url)
        return url

    def put(self):
        if self.url is None:
            self.url = self.get_unique_url(self.title)
        super(PerartModelWithTitleAndUrl, self).put()
        # Must be set after put, because the unputed is saved in memcache!!!
        memcache.set('%s-%s' % (self.__class__.name(), self.url), self) #@UndefinedVariable

    def delete(self):
        memcache.delete('%s-%s' % (self.__class__.name(), self.url)) #@UndefinedVariable
        super(PerartModelWithTitleAndUrl, self).delete()



class Program(models.Model, PerartModelWithTitleAndUrl):
    MENU_CACHE_KEY = 'program-menu'
    
    title           = models.CharField(max_length=511)
    url             = models.CharField(max_length=511, null=True, blank=True)
    subtitle        = models.CharField(max_length=511)
    text            = models.TextField(default='')
    frontpage_image = BlobField(null=True, blank=True)
    page_image      = BlobField(null=True, blank=True)
    menu            = models.TextField(default='')

    def menu_cache_key(self):
        return 'program-menu-%s' % self.url

    def get_menu(self, use_cache=True):
        if use_cache:
            menu = memcache.get(self.menu_cache_key()) #@UndefinedVariable
        else: menu = None
        if menu is None: 
            data = {'G': {}, 'P': {}}
            for gallery in self.gallery_set:
                data['G'][gallery.title.lower()] = gallery
            for project in self.project_set:
                data['P'][project.title.lower()] = project
            menu = Menu.create(self.menu, data)
            memcache.set(self.menu_cache_key(), menu) #@UndefinedVariable
        return menu

    def put(self):
        super(Program, self).put()
        memcache.delete(self.menu_cache_key()) #@UndefinedVariable

    def delete(self):
        memcache.delete(self.menu_cache_key()) #@UndefinedVariable
        for project in Project.objects.filter(program=self):
            project.program = None
            project.save()
        super(Program, self).delete()        



class Gallery(models.Model, PerartModelWithTitleAndUrl):
    program = models.ForeignKey(Program)
    title   = models.CharField(max_length=511)
    url     = models.CharField(max_length=511)

    def absolute_url(self):
        return reverse('perart.gallery', args=[self.program.url, self.url])



class Image(models.Model, PerartModel):
    gallery   = models.ForeignKey(Gallery)
    image     = BlobField(null=True, blank=True)
    thumbnail = BlobField(null=True, blank=True) 

    def create_thumbnail(self, width=74, height=31):
        img = images.Image(self.image)
        img.im_feeling_lucky()
        img_width, img_height = img.width, img.height
        if img_width / width < img_height / height:
            img.resize(width=width)
            new_height = round((float(width) / img_width) * img_height)
            img.crop(0.0, 0.0, 1.0, height/new_height)
        else:
            img.resize(height=height)
            new_width = round((float(height) / img_height) * img_width)
            img.crop(0.0, 0.0, width/new_width, 1.0)
        self.thumbnail = img.execute_transforms(output_encoding=images.JPEG)

    def url(self):
        return reverse('perart.image', args=[self.key()])

    def thumbnail_url(self):
        return reverse('perart.image', args=[self.key(), 'thumbnail'])



class Project(models.Model, PerartModelWithTitleAndUrl):
    '''Page table holds page contents'''
    program = models.ForeignKey(Program)
    title   = models.CharField(max_length=511)
    url     = models.CharField(max_length=511, null=True, blank=True) # clean url title like 'about' for 'About' etc.
    gallery = models.ForeignKey(Gallery, null=True, blank=True)
    text    = models.TextField(null=True, blank=True)

    def absolute_url(self):
        return reverse('perart.project', args=[self.program.url, self.url])



class News(models.Model, PerartModelWithTitleAndUrl):
    title     = models.CharField(max_length=511)
    url       = models.CharField(max_length=511, null=True, blank=True)
    text      = models.TextField(null=True, blank=True)
    published = models.DateField(null=True, blank=True)

    def date(self):
        return '%s %s.' % (
                ['januar', 'februar', 'mart', 'april', 'maj', 'jun', 'jul',
                 'avgust', 'septembar', 'oktobar', 'novembar', 'decembar'][self.published.month-1],
                 self.published.year)



class MenuParseError(Exception):
    def __init__(self, line_no, line, error='Error!'):
        self.line_no = line_no
        self.line = line
        self.error = error
    
    def __repr__(self):
        return u'%s! Line No: %s, Line: %s' % (self.error, self.line_no, self.line)
    __unicode__ = __str__ = __repr__



class Menu(object):
    MATCH_SOMETHING = re.compile('^(\-+)(.+?)<([lLgGpP]):(.+?)>$')
    MATCH_NOTHING   = re.compile('^(\-+)([^<>]+?)$')

    @staticmethod
    def __parse_menu(s):
        lines = []
        flines = s.splitlines()
        current_depth = 0
        current_line = 0
        for line in flines:
            current_line += 1
            line = line.strip()
            if line == '':
                continue
            match = Menu.MATCH_SOMETHING.match(line)
            if match is None:
                match = Menu.MATCH_NOTHING.match(line)
                if match is None:
                    raise MenuParseError(current_line, line)
                else:
                    items = map(string.strip, match.groups())
                    items += ['L', '#']
            else:        
                items = map(string.strip, match.groups())
            depth = len(items[0])
            if len(items) != 4:
                raise MenuParseError(current_line, line)
            if depth > current_depth + 1:
                raise MenuParseError(current_line, line, 'Invalid depth')
            items = [current_line, depth] + items[1:]
            lines.append(items)
            current_depth = depth
        return lines
    
    @staticmethod
    def __add_to_menu(menu, items, data):
        if menu.submenu is None: menu.submenu = []
        line_no, depth, name, link_type, link = items
        link_type = link_type.upper()
        if link_type == 'L':
            new_menu = Menu(parent=menu, name=name, link=link)
        elif link_type == 'G':
            try:
                new_menu = Menu(parent=menu, name=name, link=data['G'][link.lower()].absolute_url())
            except KeyError:
                raise MenuParseError(line_no, link.lower(), 'Unknown Gallery')
        elif link_type == 'P':
            try:
                new_menu = Menu(parent=menu, name=name, link=data['P'][link.lower()].absolute_url())
            except KeyError:
                raise MenuParseError(line_no, link.lower(), 'Unknown Project')
        menu.submenu.append(new_menu)
        return new_menu
    
    @staticmethod
    def create(text, data):
        items = Menu.__parse_menu(text)
        root = current_menu = last_menu = Menu()
        current_depth = 0
        for item in items:
            depth = item[1]
            if depth > current_depth:
                current_menu = last_menu
                current_depth += 1
            else:
                while depth < current_depth:
                    current_menu = current_menu.parent
                    current_depth -= 1
            last_menu = Menu.__add_to_menu(current_menu, item, data)
        return root

    def __init__(self, name=None, link=None, submenu=None, parent=None):
        self.name    = name
        self.link    = link
        self.submenu = submenu
        self.parent  = parent
    
    def spitout(self, first=True):
        s = ''
        if self.submenu:
            s += '' if first else '<ul>'
            for menu in self.submenu:
                s += '<li><a href="%s">%s</a>%s</li>' % (menu.link, menu.name, menu.spitout(False))
            s += '' if first else '</ul>' 
        return s



class Settings(models.Model):
    key   = models.CharField(max_length=255)
    value = models.TextField(default='')

    @staticmethod
    def get_main_menu_object():
        obj, _ = Settings.objects.get_or_create(key='main-menu')
        return obj

    @staticmethod
    def set_main_menu(value):
        s = Settings.get_main_menu_object()
        s.value = value
        s.save()
        memcache.delete('setting-main-menu') #@UndefinedVariable

    @staticmethod
    def get_main_menu():
        menu = memcache.get('setting-main-menu') #@UndefinedVariable
        if menu is None:
            s = Settings.get_main_menu_object()
            menu = Menu.create(s.value, {})
            memcache.set('settings-main-menu', menu) #@UndefinedVariable
        return menu
    
