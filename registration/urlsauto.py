from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^account/', include('registration.urls')),
)
