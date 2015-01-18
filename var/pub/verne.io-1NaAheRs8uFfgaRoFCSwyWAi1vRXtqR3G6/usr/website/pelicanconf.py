#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Scott Sadler'
SITENAME = u'Verne'
SITEURL = ''

PATH = '../content'

TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = u'en'

DELETE_OUTPUT_DIRECTORY = True

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# we're sorta breaking contract with the assets so disable caching to
# minimise leakage
LOAD_CONTENT_CACHE = False

from verne.web.pelicantools import VerneMarkdownReader
READERS = {'md': VerneMarkdownReader}

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),)

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#           ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

DISPLAY_CATEGORIES_ON_MENU = False

AUTHOR_SAVE_AS = ''
THEME = 'theme/verne'
