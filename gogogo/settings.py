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
gogogo.GEOHASH_PREFIX_LENGTH = 6;
gogogo.COUNTRY_CODE = "%s"
gogogo.BOUNDARY_BOX = [%f,%f,%f,%f];

// Expected Walking distance. (~ 300m)
gogogo.EXPECTED_WALKING_DISTANCE = 0.3;

""" % (django_settings.GOGOGO_DEFAULT_ZOOM,
	django_settings.GOGOGO_DEFAULT_LOCATION[0],
	django_settings.GOGOGO_DEFAULT_LOCATION[1],
    django_settings.GOGOGO_COUNTRY_CODE,
    django_settings.GOGOGO_BOUNDARY_BOX[0],
    django_settings.GOGOGO_BOUNDARY_BOX[1],
    django_settings.GOGOGO_BOUNDARY_BOX[2],
    django_settings.GOGOGO_BOUNDARY_BOX[3],
    
    )
	return ret

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    setting_converter,
)
settings.add_app_media('combined-plugins.js',
	'gogogo/jquery.treeview.min.js'
)
settings.add_app_media('combined-%(LANGUAGE_CODE)s-gogogo.js',
    
    'gogogo/jquery-ui-1.7.1.custom.min.js',
    'gogogo/jquery.layout.js',
    #Marker Manager v1.1  
    # http://gmaps-utility-library.googlecode.com/svn/trunk/markermanager/1.1/src/markermanager_packed.js
    'gogogo/markermanager_1.1_packed.js', 
    
    #Marker Clusterer v1.0
    # http://gmaps-utility-library.googlecode.com/svn/trunk/markerclusterer/1.0/src/markerclusterer_packed.js
    #'gogogo/markerclusterer_v1.0_packed.js',
    
    'gogogo/geohash.js',
    
	#core 
    #setting_converter,
	
	#Gogogo javascript
    'gogogo/utils.js',
	'gogogo/map.js',
	'gogogo/SearchingManager.js',
	'gogogo/Model.js',
	'gogogo/ModelManager.js',
	'gogogo/Stop.js',
	'gogogo/StopManager.js',
	'gogogo/Shape.js',
    'gogogo/Cluster.js',
	'gogogo/ClusterManager.js',
	'gogogo/Trip.js',
	'gogogo/Address.js',
	'gogogo/Planner.js',
    'gogogo/StopListEditor.js',
    # ...
)

settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'gogogo/gogogo.css',
    # ...
)
settings.add_app_media('combined-plugins.css',
	'gogogo/jquery.treeview.css',
)
