from django.contrib.auth import authenticate
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db import IntegrityError
from django.conf import settings
from rest_framework.decorators import api_view,authentication_classes,permission_classes,action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from petdetective_backend.serializers import *
from .models import *
from .serializers import *

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test(request):
    return Response("HELLO", status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_pet(request):
    #Check owner
    if request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Only owners can add pets.")).data, status=status.HTTP_403_FORBIDDEN)
    name=request.data['name']
    description=request.data['description']
    last_seen = request.data['lastSeen']
    animal = request.data['animal']
    lat = request.data['lat']
    lng = request.data['lng']
    picture = request.FILES['picture']

    #Create pet
    try:
        pet = Pet(
            owner = request.user,
            name = name,
            description=description,
            last_seen = last_seen,
            animal = animal,
            picture = picture
        )
        pet.full_clean()
        pet.save()
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to add pet.")).data, status=status.HTTP_400_BAD_REQUEST)
    #Create location
    try:
        location = PetLocation.objects.create(
            point = 'POINT(%s %s)' % (lng, lat),
            pet = pet
        )
    except Exception as e:
        print(e)
        pet.delete()
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to add location.")).data, status=status.HTTP_400_BAD_REQUEST)
    serializer = PetSerializer(pet)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_pet_location(request):
    try:
        lat = request.data['lat']
        lng = request.data['lng']
        type = request.data['type']
        pet = Pet.objects.get(id=request.data['pet_id'])
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Invalid data.")).data, status=status.HTTP_400_BAD_REQUEST)
    try:
        location = PetLocation.objects.create(
            pet = pet,
            location_type = type,
            point = 'POINT(%s %s)' % (lng, lat),
        )
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Status type already exists for this pet.")).data, status=status.HTTP_400_BAD_REQUEST)
    serializer = PetLocationSerializer(location)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_location(request):
    lat = request.data['lat']
    lng = request.data['lng']
    if request.user.is_detective:
        try:
            location = DetectiveLocation.objects.create(
                detective = request.user,
                point = 'POINT(%s %s)' % (lng, lat),
            )
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to add location.")).data, status=status.HTTP_400_BAD_REQUEST)
        serializer = DetectiveLocationSerializer(location)
    else:
        try:
            location = OwnerLocation.objects.create(
                owner = request.user,
                point = 'POINT(%s %s)' % (lng, lat),
            )
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to add location.")).data, status=status.HTTP_400_BAD_REQUEST)
        serializer = OwnerLocationSerializer(location)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owners_near_me(request):
    try:
        distance = request.query_params['dist']
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Invalid data.")).data, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not a detective.")).data, status=status.HTTP_400_BAD_REQUEST)
    detective_location = request.user.detectivelocation_set.all()
    if len(detective_location) > 0:
        point = detective_location[0].point
    else:
        return Response(ResponseSerializer(GeneralResponse(False,"Location is not set.")).data, status=status.HTTP_400_BAD_REQUEST)
    owners = Account.objects.filter(ownerlocation__point__distance_lte=(point,int(distance)*1000),is_detective=False)
    serializer = UserSerializer(owners,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detectives_near_me(request):
    try:
        distance = request.query_params['dist']
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Invalid data.")).data, status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not a detective.")).data, status=status.HTTP_403_FORBIDDEN)
    owner_location = request.user.ownerlocation_set.all()
    if len(owner_location) > 0:
        point = owner_location[0].point
    else:
        return Response(ResponseSerializer(GeneralResponse(False,"Location is not set.")).data, status=status.HTTP_400_BAD_REQUEST)
    detectives = Account.objects.filter(detectivelocation__point__distance_lte=(point,int(distance)*1000),is_detective=True)
    serializer = UserSerializer(detectives,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def pets_near_me(request):
    try:
        lat = request.query_params['lat']
        lng = request.query_params['lng']
        distance = request.query_params['dist']
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Invalid data.")).data, status=status.HTTP_400_BAD_REQUEST)
    point = Point(float(lng), float(lat),srid=4326)
    pets = Pet.objects.filter(petlocation__point__distance_lte=(point,int(distance)*1000),petlocation__location_type=0)
    serializer = PetSerializer(pets,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_case(request):
    if not request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not a detective.")).data, status=status.HTTP_403_FORBIDDEN)
    try:
        description = request.data['description']
        pet = Pet.objects.get(id=request.data['pet_id'],status=0)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Invalid data.")).data, status=status.HTTP_400_BAD_REQUEST)
    try:
        request = Request.objects.create(
            detective = request.user,
            pet = pet,
            accepted = False,
            description = description
        )
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to create request.")).data, status=status.HTTP_400_BAD_REQUEST)
    serializer = RequestSerializer(request)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_request(request):
    if request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not an owner.")).data, status=status.HTTP_403_FORBIDDEN)
    try:
        req = Request.objects.get(id=request.data['id'])
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Request not found.")).data, status=status.HTTP_404_NOT_FOUND)
    if not req.pet.owner == request.user:
        return Response(ResponseSerializer(GeneralResponse(False,'Denied - you are not the owner.')).data, status=status.HTTP_403_FORBIDDEN)
    req.accepted = True
    req.save()
    #Create a case
    try:
        case = Case.objects.create(
            detective = req.detective,
            pet = req.pet,
            request = req,
        )
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Able to accept request, but case was not created.")).data, status=status.HTTP_400_BAD_REQUEST)
    serializer = CaseSerializer(case)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_requests(request):
    result_set_type = request.query_params.get('qstype','all')
    if request.user.is_detective:
        try:
            if result_set_type == 'accepted':
                reqs = Request.objects.filter(detective=request.user, accepted=True)
            elif result_set_type == 'pending':
                reqs = Request.objects.filter(detective=request.user, accepted=False)
            else:
                reqs = Request.objects.filter(detective=request.user)
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            if result_set_type == 'accepted':
                reqs = Request.objects.filter(pet__owner=request.user, accepted=True)
            elif result_set_type == 'pending':
                reqs = Request.objects.filter(pet__owner=request.user, accepted=False)
            else:
                reqs = Request.objects.filter(pet__owner=request.user)
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = RequestSerializer(reqs,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_offers(request):
    if request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not an owner.")).data, status=status.HTTP_403_FORBIDDEN)
    try:
        reqs = Request.objects.filter(pet__owner=request.user)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = RequestSerializer(reqs,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_cases(request):
    try:
        if request.user.is_detective:
            cases = Case.objects.filter(detective=request.user)
        else:
            cases = Case.objects.filter(pet__owner=request.user)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = CaseSerializer(cases,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_cases(request):
    try:
        owner = Account.objects.get(id=request.query_params['owner_id'])
        if owner.is_detective:
            return Response(ResponseSerializer(GeneralResponse(False,"Owner not found.")).data, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Owner not found.")).data, status=status.HTTP_404_NOT_FOUND)
    try:
        cases = Case.objects.filter(pet__owner=owner)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = CaseSerializer(cases,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_pets(request):
    if request.user.is_detective:
        return Response(ResponseSerializer(GeneralResponse(False,"Not an owner.")).data, status=status.HTTP_403_FORBIDDEN)
    pets = Pet.objects.filter(owner=request.user)
    serializer = PetSerializer(pets,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pet_requests(request):
    id=request.query_params['pet_id']
    try:
        reqs = Request.objects.filter(pet__id=id, accepted=False)
        #reqs = Request.objects.all()
        #print(reqs)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = RequestSerializer(reqs,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pet_cases(request):
    id=request.query_params['pet_id']
    try:
        cases = Case.objects.filter(pet__id=id)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve requests.")).data, status=status.HTTP_404_NOT_FOUND)
    serializer = CaseSerializer(cases,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
