from django.conf import settings

def maps_api_key(request):
	return {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY,
		'GOGOGO_DEFAULT_LOCATION' : settings.GOGOGO_DEFAULT_LOCATION,
		'GOGOGO_DEFAULT_ZOOM' : settings.GOGOGO_DEFAULT_ZOOM
	}

