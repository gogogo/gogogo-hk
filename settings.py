# -*- coding: utf-8 -*-
from ragendja.settings_pre import *
import settings_private

# Increase this when you update your media on the production site, so users
# don't have to refresh their cache. By setting this your MEDIA_URL
# automatically becomes /media/MEDIA_VERSION/
MEDIA_VERSION = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = settings_private.KEY

#ENABLE_PROFILER = True
#ONLY_FORCED_PROFILE = True
#PROFILE_PERCENTAGE = 25
#SORT_PROFILE_RESULTS_BY = 'cumulative' # default is 'time'
#PROFILE_PATTERN = 'ext.db..+\((?:get|get_by_key_name|fetch|count|put)\)'

# Enable I18N and set default language to 'en'
USE_I18N = True
LANGUAGE_CODE = 'en'

#Restrict supported languages (and JS media generation)
LANGUAGES = (
#    ('de', 'German'),
    ('en', 'English'),
    ('zh-tw',u'繁體中文'),
    ('zh-cn',u'简体中文')
)

# Can not put into the bottom of the file. It will raise unexcepted result
COMBINE_MEDIA = {
    'combined-%(LANGUAGE_CODE)s.js': (
        # See documentation why site_data can be useful:
        # http://code.google.com/p/app-engine-patch/wiki/MediaGenerator
        '.site_data.js',
    ),
	'combined-%(LANGUAGE_CODE)s-gogogo.js': (
        # See documentation why site_data can be useful:
        # http://code.google.com/p/app-engine-patch/wiki/MediaGenerator
        '.site_data.js',
    ),
    'combined-%(LANGUAGE_DIR)s.css': (
        'global/gogogo-hk.css',
    ),
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'gogogo.context_processors.maps_api_key'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Django authentication

    #'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Google authentication
    'ragendja.auth.middleware.GoogleAuthenticationMiddleware',
    # Hybrid Django/Google authentication
    #'ragendja.auth.middleware.HybridAuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'ragendja.sites.dynamicsite.DynamicSiteIDMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

# Google authentication
AUTH_USER_MODULE = 'ragendja.auth.google_models'
AUTH_ADMIN_MODULE = 'ragendja.auth.google_admin'
# Hybrid Django/Google authentication
#AUTH_USER_MODULE = 'ragendja.auth.hybrid_models'

GLOBALTAGS = (
    'ragendja.templatetags.ragendjatags',
    'django.templatetags.i18n',
)

LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = [
    #This will add jquery to your COMBINE_MEDIA['combined-%(LANGUAGE_CODE)s.js'] automatically
    'jquery',
    
    # Add blueprint CSS (http://blueprintcss.org/)
    'blueprintcss',

    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sites',
    'appenginepatcher',
#    'myapp',
#    'registration',
    'mediautils',
    'gogogo',

           
]

# List apps which should be left out from app settings and urlsauto loading
IGNORE_APP_SETTINGS = IGNORE_APP_URLSAUTO = (
    # Example:
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'yetanotherapp',
)

from ragendja.settings_post import *

DEFAULT_CHARSET="utf-8"

###########
# gaebar #
###########

GAEBAR_LOCAL_URL = 'http://localhost:8000'

GAEBAR_SERVERS = {
  u'Deployment': u'http://test.gogogo.hk', 
  u'Staging': u'http://gogogo-staging.appspot.com', 
  u'Local Test': u'http://localhost:8080',
}

GAEBAR_MODELS = (
     (
          'gogogo.models', 
          (u'Agency',u'Stop',u'Route',u'Trip',u'Changelog',u'Cluster'),
     ),
)

try:
    GAEBAR_SECRET_KEY = settings_private.GAEBAR_SECRET_KEY
except AttributeError:
    ENABLE_GAEBAR = False
else:
    ENABLE_GAEBAR = True # Enable gaebar only if the secret key is set
    INSTALLED_APPS.append("gaebar")

GAE_BACKUP_MODELS = (
    (
        'django.contrib.auth.models',
        ('auth_user',)
    ),
     (
         'gogogo.models', 
        ('gogogo_agency','gogogo_stop','gogogo_route','gogogo_trip','gogogo_changelog',
        'gogogo_shape','gogogo_cluster',
        'gogogo_faretrip',
        'gogogo_farestop',
        'gogogo_farepair',
        'gogogo_transfer'
        ),
     ),
)

###########
# Gogogo #
###########

GOOGLE_MAPS_KEY = settings_private.GOOGLE_MAPS_KEY

#Default location 
GOGOGO_DEFAULT_LOCATION=[22.3, 114.167]
GOGOGO_DEFAULT_ZOOM=10
