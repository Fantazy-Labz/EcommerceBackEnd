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