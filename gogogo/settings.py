from ragendja.settings_post import settings
from django.conf import settings as django_settings

def setting_converter(**kwargs):
	"""
	Generate default setting for gogogo javascript
	"""
	ret = """
var gogogo = {}
gogogo.DEFAULT_ZOOM=%d;
gogogo.DEFAULT_LOCATION = [%f,%f];
""" % (django_settings.GOGOGO_DEFAULT_ZOOM,
	django_settings.GOGOGO_DEFAULT_LOCATION[0],
	django_settings.GOGOGO_DEFAULT_LOCATION[1])
	return ret

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'gogogo/jquery-ui-1.7.1.custom.min.js',
    'gogogo/jquery.layout.js',
    
    #Gogogo javascript
    setting_converter,
	'gogogo/map.js',
    # ...
)

settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'gogogo/gogogo.css',
    # ...
)
