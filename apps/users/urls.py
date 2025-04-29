from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    AdressListView,
    AdressDetailView,
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    UserProfileView,
)

urlpatterns = [
    # Rutas de usuario
    path('users/', UserListView.as_view(), name='user_list'),  # Listado y creación de usuarios
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),  # Detalles, actualización y eliminación de usuario

    # Rutas de direcciones
    path('addresses/', AdressListView.as_view(), name='address_list'),  # Listado y creación de direcciones
    path('addresses/<int:pk>/', AdressDetailView.as_view(), name='address_detail'),  # Detalles, actualización y eliminación de dirección

    # Rutas de autenticación
    path('register/', RegisterView.as_view(), name='register'),  # Registro de usuario
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),  # Confirmación de email
    path('login/', LoginView.as_view(), name='login'),  # Inicio de sesión
    path('logout/', LogoutView.as_view(), name='logout'),  # Cierre de sesión

    # Perfil de usuario
    path('profile/', UserProfileView.as_view(), name='user_profile'),  # Ver, editar y eliminar el perfil del usuario
]
