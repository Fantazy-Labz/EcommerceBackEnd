from django.urls import path
from .views import (
    UserListView, UserDetailView,
    AdressListView, AdressDetailView,
)

urlpatterns = [
    # Usuarios
    path('users/', UserListView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Direcciones
    path('adresses/', AdressListView.as_view(), name='adress-list-create'),
    path('adresses/<int:pk>/', AdressDetailView.as_view(), name='adress-detail'),
]