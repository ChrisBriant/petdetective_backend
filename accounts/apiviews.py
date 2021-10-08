from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.conf import settings
from rest_framework.decorators import api_view,authentication_classes,permission_classes,action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.tokens import RefreshToken
from password_validator import PasswordValidator
from .models import *
from .email import sendpasswordresetemail,sendjoiningconfirmation
from petdetective_backend.serializers import *


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



@api_view(['POST','OPTIONS'])
def get_token(request):
    if request.method == "POST":
        try:
            email = request.data["email"]
            password = request.data["password"]
            user = authenticate(username=email,password=password)
            if user:
                if user.is_enabled:
                    #Issue token
                    token = get_tokens_for_user(user)
                    return Response(token, status=status.HTTP_200_OK)
                else:
                    return Response(ResponseSerializer(GeneralResponse(False,"User is not enabled")).data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ResponseSerializer(GeneralResponse(False,"User name or password are incorrect")).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve token")).data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    password = request.data['password']
    passchk = request.data['passchk']
    username = request.data['username']
    email = request.data['email']
    is_detective =  request.data.get('is_detective',False)

    # Create a schema
    schema = PasswordValidator()
    schema\
    .min(8)\
    .max(100)\
    .has().uppercase()\
    .has().lowercase()\
    .has().digits()\
    .has().no().spaces()\

    if password != passchk or not schema.validate(password):
        return Response(ResponseSerializer(GeneralResponse(False,'Password does not meet the complexity requirements.')).data, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = Account.objects.create_user (email,username,password)
        #Get joining confirmation information over to user
        user.hash = hex(random.getrandbits(128))
        user.is_detective = is_detective
        user.save()
        url = settings.BASE_URL + "confirm/" + user.hash + "/"
        sendjoiningconfirmation(url,user.email,user.name,'CONFIRM_ACCOUNT_EMAIL')
        return Response(ResponseSerializer(GeneralResponse(True,'Account Created')).data, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        print(type(e).__name__)
        return Response(ResponseSerializer(GeneralResponse(False,'Email already exists with us, please try a different one or send a forgot password request')).data, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(ResponseSerializer(GeneralResponse(False,'Problem creating account')).data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgot_password(request):
    email = request.data['email']
    try:
        user = Account.objects.get(email=email)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Email address not found, please register a new account.')).data, status=status.HTTP_400_BAD_REQUEST)
    user.hash = hex(random.getrandbits(128))
    user.save()
    url = settings.BASE_URL + "passwordreset/" + user.hash + "/"
    sendpasswordresetemail(url,user.email,user.name,'RESET_PASSWORD_EMAIL')
    return Response(ResponseSerializer(GeneralResponse(True,'Please check your email and click on the link to reset your password')).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password(request):
    password = request.data['password']
    hash = request.data['hash']
    try:
        user = Account.objects.get(hash=hash)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Sorry, unable to reset password')).data, status=status.HTTP_400_BAD_REQUEST)
    user.hash = ''
    user.set_password(password)
    user.save()
    return Response(ResponseSerializer(GeneralResponse(True,'Password succesfully changed')).data, status=status.HTTP_200_OK)
