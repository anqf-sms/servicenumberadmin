from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
import portal.views as views

urlpatterns = [
    url(r'^servicesettings$', views.get_service_settings, name='get_service_settings'),
]

