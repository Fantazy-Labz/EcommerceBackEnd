from .models import User, Address
from apps.users.permisions import OnlyAdminOrCurrentUser, OnlyAdmin
from rest_framework import generics
from .serializers import UserSerializer, AdressSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

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

    queryset = Address.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdmin ]

class AdressDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Address.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdminOrCurrentUser ]

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })

class LogoutView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response(status=status.HTTP_200_OK)