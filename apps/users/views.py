from .models import User, Address
from apps.users.permisions import OnlyAdmin
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .serializers import UserSerializer, AdressSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from django.template.loader import render_to_string
from django.urls import reverse
import os
import uuid

# Create your views here.
class UserListView(generics.ListCreateAPIView):

    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    permission_classes = [ OnlyAdmin ]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    permission_classes = [ OnlyAdmin ]

class AdressListView(generics.ListCreateAPIView):

    queryset = Address.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdmin ]

class AdressDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Address.objects.all().order_by('created_at')
    serializer_class = AdressSerializer
    permission_classes = [ OnlyAdmin ]

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.verification_token = uuid.uuid4()
            user.save()

            # Ahora que ya existe el token, podemos hacer el reverse
            relative_link = reverse('verify-email', kwargs={'token': str(user.verification_token)})
            domain = os.environ.get('DOMAIN')  
            confirmation_link = f"{domain}{relative_link}"

            html_content = render_to_string('confirm_email.html', {
                'username': user.username,
                'domain': 'http://localhost:8000/',
                'token': user.verification_token,
            })


            email = EmailMultiAlternatives(
                subject='Confirma tu correo',
                body='Por favor confirma tu correo.',
                from_email=os.environ.get('EMAIL_HOST_USER'),
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return Response({
                'message': 'Usuario registrado. Revisa tu correo para confirmar tu cuenta.',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_active = True
            user.is_email_verified = True
            user.verification_token = None  # Limpias el token
            user.save()
            return Response({'message': 'Correo verificado. Ya puedes iniciar sesión.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Token inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)



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
    

class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)