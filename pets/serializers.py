from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import *
from django.conf import settings


class PetLocationSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    location_type = serializers.SerializerMethodField()

    class Meta:
        model = PetLocation
        fields = ('id','point','lat','lng','location_type')

    def get_lat(self,obj):
        lng, lat = obj.point.coords
        return lat

    def get_lng(self,obj):
        lng, lat = obj.point.coords
        return lng

    def get_location_type(self,obj):
        return location_types[obj.location_type]

class OwnerLocationSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = OwnerLocation
        fields = ('id','point','lat','lng')

    def get_lat(self,obj):
        lng, lat = obj.point.coords
        return lat

    def get_lng(self,obj):
        lng, lat = obj.point.coords
        return lng

class DetectiveLocationSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = DetectiveLocation
        fields = ('id','point','lat','lng')

    def get_lat(self,obj):
        lng, lat = obj.point.coords
        return lat

    def get_lng(self,obj):
        lng, lat = obj.point.coords
        return lng


class PetSerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = ('id','name','description','last_seen','animal','picture','status','locations','date_added','date_modified')

    def get_locations(self,obj):
        return PetLocationSerializer(obj.petlocation_set.all(),many=True).data


class UserSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id','name','is_detective','location')

    def get_location(self,obj):
        if obj.is_detective:
            return DetectiveLocationSerializer(obj.detectivelocation_set.all()[0]).data
        else:
            return OwnerLocationSerializer(obj.ownerlocation_set.all()[0]).data

class RequestSerializer(serializers.ModelSerializer):
    detective = UserSerializer()
    pet = PetSerializer()

    class Meta:
        model = Request
        fields = ('id','detective','pet','description','accepted','date_added','date_modified')
        
