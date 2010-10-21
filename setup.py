__author__    = 'Viktor Kerkez <alefnula@gmail.com>'
__contact__   = 'alefnula@gmail.com'
__date__      = '24 January 2010'
__copyright__ = 'Copyright (c) 2010 Viktor Kerkez'

from distutils.core import setup

setup(
    name             = 'TeacupCMS',
    version          = '0.0.1',
    description      = 'TeacupCMS',
    long_description = 'TeacupCMS is a lightweight CMS designed to run on Google App Engine.',
    platforms        = ['Windows', 'POSIX', 'MacOS'],
    author           = 'Viktor Kerkez',
    author_email     = 'alefnula@gmail.com',
    maintainer       = 'Viktor Kerkez',
    maintainer_email = 'alefnula@gmail.com',
    url              = 'http://bitbucket.org/alefnula/teacupcms/',
    license          = 'GPLv3',
    package_dir      = {'' : 'src'},
    packages         = [
                        'perart',
                       ],
   package_data      = {
                        'perart' : [
                                       'templates/perart/*.html',
                                      ],
                       },
)
