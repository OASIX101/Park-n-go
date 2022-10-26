from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access all users but gives special permissions to admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            
            return True
        
        else:
            if request.user.is_authenticated and request.user.is_staff == True:
                return True

            return False
        


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Allows access all users but gives special permissions to admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            
            return True
        
        else:
            if request.user.is_authenticated:
                return True
                
            return False
        
class IsUserAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):

        if request.user and request.user.is_authenticated == True:
            return True
        else:
            raise PermissionDenied(detail= {"message": "Permission denied"})