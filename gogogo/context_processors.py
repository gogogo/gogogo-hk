from django.conf import settings

def maps_api_key(request):
	return {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY}

