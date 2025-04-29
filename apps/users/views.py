from django.shortcuts import render
from .models import User, Adress
from apps.users.permisions import OnlyAdminOrCurrentUser, OnlyAdmin
from rest_framework import generics
from .serializers import UserSerializer, AdressSerializer

# Create your views here.
class UserListView(generics.ListCreateAPIView):

    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    permission_classes = [ OnlyAdmin ]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    permission_classes = [ OnlyAdminOrCurrentUser ]

class AdressListView(generics.ListCreateAPIView):

    queryset = Adress.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdmin ]

class AdressDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Adress.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdminOrCurrentUser ]