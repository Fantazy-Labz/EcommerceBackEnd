from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly:

    def has_permission(self, request, view):
        
        if request.user and request.user.is_superuser:
            return True

        return request.method in ['GET', 'HEAD', 'OPTIONS']
    

class OnlyAdmin:

    def has_permission(señf, request):
        
        if request.user and request.user.is_superuser:
            return True

        return False

class OnlyAdminOrCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Solo permite si es superusuario o si es el dueño del objeto
        return request.user.is_superuser or obj.id == request.user.id