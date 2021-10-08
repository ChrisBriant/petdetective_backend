from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from django.db.models import Count, Avg
from accounts.models import Account
from django.conf import settings

class GeneralResponse(object):
    def __init__(self, success, message):
        self.success = success
        self.message = message

class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=100)
