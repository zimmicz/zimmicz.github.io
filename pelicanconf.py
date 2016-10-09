#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Michal Zimmermann'
SITENAME = u'Michal Zimmermann'
SITESUBTITLE = u'Pieces of knowledge from the world of GIS.'
SITEURL = ''

PATH = 'content'
THEME = 'content/theme/simple'
TIMEZONE = 'Europe/Prague'

DEFAULT_LANG = u'en'
DEFAULT_DATE = None
TYPOGRIFY = True
# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_ALL_RSS = 'feed.xml'

# Blogroll
LINKS = ()

# Social widget
SOCIAL = ()

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Customized settings
STATIC_PATHS = ['assets']
ARTICLE_URL = 'posts/{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{slug}/index.html'
READERS = {'html': None}
CSS_FOUNDATION = 'foundation.min.css'
CSS_NORMALIZE = 'normalize.css'
CSS_FILE = 'screen.css'
LOCALE = 'en_US.UTF-8'
CATEGORIES_SAVE_AS = 'categories/index.html'
TAGS_SAVE_AS = 'tags/index.html'

PLUGIN_PATHS = ['content/plugins']
PLUGINS = ['neighbors', 'assets']