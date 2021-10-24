from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views
from . import apiviews
from .customtoken import CustomTokenObtainPairView

urlpatterns = [
	#Authenticate to be taken out after testing /autneticate which has the custom claims
	url(r'^refresh/',jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
	#url(r'^authenticate/',apiviews.get_token, name='authenticate'),
	url(r'^authenticate/',CustomTokenObtainPairView.as_view(), name='authenticate'),
	url(r'^register/$', apiviews.register, name='register'),
	url(r'^forgotpassword/$', apiviews.forgot_password, name='forgotpassword'),
	url(r'^changepassword/$', apiviews.change_password, name='changepassword'),
	url(r'^myprofile/$', apiviews.my_profile, name='myprofile'),
]
