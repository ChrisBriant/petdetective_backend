from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import *
from django.conf import settings
import json

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
    is_case_open = serializers.SerializerMethodField()
    requests_detective_id = serializers.SerializerMethodField()
    status_str = serializers.SerializerMethodField()


    class Meta:
        model = Pet
        fields = ('id','name','description','last_seen','animal','picture',
        'status','status_str','locations','date_added','date_modified','is_case_open',
        'requests_detective_id')

    def get_locations(self,obj):
        return PetLocationSerializer(obj.petlocation_set.all(),many=True).data

    def get_is_case_open(self,obj):
        if len(obj.case_set.all()) > 0:
            return True
        else:
            return False

    def get_requests_detective_id(self,obj):
        return json.dumps([r.detective.id for r in list(obj.request_set.all())])

    def get_status_str(self,obj):
        return pet_statuses[obj.status]


class UserSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    request_count = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id','name','is_detective','location','request_count','case_count')

    def get_location(self,obj):
        if obj.is_detective:
            locations = obj.detectivelocation_set.all()
            if len(locations) > 0:
                return DetectiveLocationSerializer(obj.detectivelocation_set.all()[0]).data
        else:
            locations = obj.ownerlocation_set.all()
            if len(locations) > 0:
                return OwnerLocationSerializer(obj.ownerlocation_set.all()[0]).data

    def get_request_count(self,obj):
        if obj.is_detective:
            return obj.request_set.all().count()
        else:
            return Request.objects.select_related('pet').filter(pet__owner=obj).count()

    def get_case_count(self,obj):
        if obj.is_detective:
            return obj.case_set.all().count()
        else:
            return Case.objects.select_related('pet').filter(pet__owner=obj).count()

class RequestSerializer(serializers.ModelSerializer):
    detective = UserSerializer()
    pet = PetSerializer()

    class Meta:
        model = Request
        fields = ('id','detective','pet','description','accepted','date_added','date_modified')

class CaseSerializer(serializers.ModelSerializer):
    detective = UserSerializer()
    pet = PetSerializer()
    request_id = serializers.ReadOnlyField(source='request.id')

    class Meta:
        model = Request
        fields = ('id','detective','pet','request_id','date_added','date_modified')
