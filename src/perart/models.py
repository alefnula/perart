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
    FIELD_LIST  = []
    ACTION_LIST = []
    
    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def get_list_url(cls):
        return reverse('perart.admin.%s.list' % cls.name().lower())

    @classmethod
    def get_add_url(cls):
        return reverse('perart.admin.%s.edit' % cls.name().lower())

    def get_edit_url(self):
        return reverse('perart.admin.%s.edit' % self.name().lower(), args=[self.id])
    
    def get_delete_url(self):
        return reverse('perart.admin.%s.delete' % self.name().lower(), args=[self.id])




class PerartModelWithTitleAndUrl(PerartModel):
    def __unicode__(self):
        return self.title    

    @classmethod
    def get_by_url(cls, url):
        obj = memcache.get('%s-%s' % (cls.name(), url)) #@UndefinedVariable
        if obj is None:
            try:
                obj = cls.objects.get(url=url)
                memcache.set('%s-%s' % (cls.name(), url), obj) #@UndefinedVariable
            except cls.DoesNotExist: pass
        return obj

    @classmethod
    def get_unique_url(cls, old_url, title):
        '''Function takes in an url and checks if it's already used.
        
        If the url already exists then adds a number to the end of the url.
        '''
        url = unicode(slugify(title))
        if url == old_url: return url
        nr = 0
        obj = cls.get_by_url(url)
        while obj:
            nr += 1
            url = '%s-%s' % (url, nr)
            obj = cls.get_by_url(url)
        return url

    def save(self, *args, **kwargs):
        self.url = self.get_unique_url(self.url, self.title)
        # Must be set after put, because the unputed is saved in memcache!!!
        memcache.set('%s-%s' % (self.__class__.name(), self.url), self) #@UndefinedVariable

    def delete(self):
        memcache.delete('%s-%s' % (self.__class__.name(), self.url)) #@UndefinedVariable
        super(PerartModelWithTitleAndUrl, self).delete()



class Program(PerartModelWithTitleAndUrl, models.Model):
    MENU_CACHE_KEY = 'program-menu' 
    FIELD_LIST = [
        {'name': 'title', 'width': 350},
    ]
    ACTION_LIST = [
        {'name': 'Edit Menu', 'action': 'get_edit_menu_url'},
    ]
    
    title           = models.CharField(max_length=511)
    url             = models.CharField(max_length=511, null=True, blank=True)
    subtitle        = models.CharField(max_length=511)
    text            = models.TextField(default='')
    frontpage_image = BlobField(null=True, blank=True)
    page_image      = BlobField(null=True, blank=True)
    menu            = models.TextField(default='')


    # Actions
    @property
    def get_edit_menu_url(self):
        return reverse('perart.admin.program.menu_edit', args=[self.id])

    def menu_cache_key(self):
        return 'program-menu-%s' % self.url

    def get_menu(self, use_cache=True):
        if use_cache:
            menu = memcache.get(self.menu_cache_key()) #@UndefinedVariable
        else: menu = None
        if menu is None: 
            data = {'G': {}, 'P': {}}
            for gallery in self.galleries:
                data['G'][gallery.title.lower()] = gallery
            for project in self.projects:
                data['P'][project.title.lower()] = project
            menu = Menu.create(self.menu, data)
            memcache.set(self.menu_cache_key(), menu) #@UndefinedVariable
        return menu

    def save(self, *args, **kwargs):
        PerartModelWithTitleAndUrl.save(self)
        models.Model.save(self, *args, **kwargs)
        memcache.delete(self.menu_cache_key()) #@UndefinedVariable

    def delete(self):
        memcache.delete(self.menu_cache_key()) #@UndefinedVariable
        for project in Project.objects.filter(program=self):
            project.program = None
            project.save()
        super(Program, self).delete()        


    @property
    def projects(self):
        return Project.objects.filter(program=self)
    
    @property
    def galleries(self):
        return Gallery.objects.filter(program=self)



class Gallery(PerartModelWithTitleAndUrl, models.Model):
    FIELD_LIST    = [
        {'name': 'title',   'width': 350},
    ]
    
    program = models.ForeignKey(Program)
    title   = models.CharField(max_length=511)
    url     = models.CharField(max_length=511)

    @property
    def images(self):
        return Image.objects.filter(gallery=self)

    def absolute_url(self):
        return reverse('perart.gallery', args=[self.program.url, self.url])

    def save(self, *args, **kwargs):
        PerartModelWithTitleAndUrl.save(self)
        models.Model.save(self, *args, **kwargs)



class Image(PerartModel, models.Model):
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
        return reverse('perart.image', args=[self.id])

    def thumbnail_url(self):
        return reverse('perart.image', args=[self.id, 'thumbnail'])



class Project(PerartModelWithTitleAndUrl, models.Model):
    FIELD_LIST    = [
        {'name': 'title',   'width': 350},
        {'name': 'program', 'width': 120}
    ]
    
    program = models.ForeignKey(Program)
    title   = models.CharField(max_length=511)
    url     = models.CharField(max_length=511, null=True, blank=True) # clean url title like 'about' for 'About' etc.
    gallery = models.ForeignKey(Gallery, null=True, blank=True)
    text    = models.TextField(null=True, blank=True)

    def absolute_url(self):
        return reverse('perart.project', args=[self.program.url, self.url])

    def save(self, *args, **kwargs):
        PerartModelWithTitleAndUrl.save(self)
        models.Model.save(self, *args, **kwargs)



class News(PerartModelWithTitleAndUrl, models.Model):
    FIELD_LIST = [
        {'name': 'title',     'width': 350},
        {'name': 'published', 'width': 120}
    ]
    
    title     = models.CharField(max_length=511)
    url       = models.CharField(max_length=511, null=True, blank=True)
    text      = models.TextField(null=True, blank=True)
    published = models.DateField(null=True, blank=True)

    def date(self):
        return '%s %s.' % (
                ['januar', 'februar', 'mart', 'april', 'maj', 'jun', 'jul',
                 'avgust', 'septembar', 'oktobar', 'novembar', 'decembar'][self.published.month-1],
                 self.published.year)

    def save(self, *args, **kwargs):
        PerartModelWithTitleAndUrl.save(self)
        models.Model.save(self, *args, **kwargs)


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
    
