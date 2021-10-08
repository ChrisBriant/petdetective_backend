from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
	url(r'^addpet/',add_pet, name='addpet'),
    url(r'^addlocation/',add_location, name='addlocation'),
	url(r'^addpetlocation/',add_pet_location, name='addpetlocation'),
	url(r'^petsnearme',pets_near_me, name='petsnearme'),
	url(r'^ownersnearme',owners_near_me, name='ownersnearme'),
	url(r'^makerequest/',request_case, name='makerequest'),
	url(r'^detectivesnearme',detectives_near_me, name='detectivessnearme'),
    url(r'^test/',test, name='test'),
]
