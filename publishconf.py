#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

CATEGORY_FEED_ATOM = None
DELETE_OUTPUT_DIRECTORY = False
FEED_ALL_ATOM = 'atom.xml'
FEED_ALL_RSS = 'feed.xml'
FEED_DOMAIN = SITEURL
OUTPUT_PATH = 'posts/'
PRODUCTION = True
RELATIVE_URLS = False
SITEURL = 'https://www.zimmi.cz/posts'
THEME = 'content/theme/simple'
TYPOGRIFY = True

# Following items are often useful when publishing

ARTICLE_URL = '{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{slug}/index.html'
GOOGLE_ANALYTICS = True
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['neighbors', 'assets', 'related_posts', 'series']

CACHE_CONTENT = True
LOAD_CONTENT_CACHE = True
CACHE_PATH = 'cache'
CHECK_MODIFIED_METHOD = 'mtime'
IMAGE_OPTIMIZATION_ONCE_AND_FOR_ALL = True

IGNORE_FILES = ['*.rst', 'pelican-plugins/**/*.md']
