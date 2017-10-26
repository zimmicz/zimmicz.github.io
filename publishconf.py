#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'https://www.zimmi.cz/posts'
RELATIVE_URLS = False
THEME = 'content/theme/simple'
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'atom.xml'
CATEGORY_FEED_ATOM = None
FEED_ALL_RSS = 'feed.xml'
OUTPUT_PATH = 'posts/'
DELETE_OUTPUT_DIRECTORY = False
TYPOGRIFY = True

# Following items are often useful when publishing

ARTICLE_URL = '{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{slug}/index.html'
GOOGLE_ANALYTICS = True
PLUGIN_PATHS = ['content/pelican-plugins']
PLUGINS = ['neighbors', 'assets', 'pelican-image-optimizer', 'related_posts', 'series']

CACHE_CONTENT = True
LOAD_CONTENT_CACHE = True
CACHE_PATH = 'cache'
CHECK_MODIFIED_METHOD = 'mtime'
IMAGE_OPTIMIZATION_ONCE_AND_FOR_ALL = True

IGNORE_FILES = ['*.rst', 'pelican-plugins/**/*.md']
