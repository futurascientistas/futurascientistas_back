from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class IsAdminOrAvaliadora(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['admin', 'avaliadora']).exists()

class IsSelfOrAdminOrAvaliadora(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj == request.user or request.user.groups.filter(name__in=['admin', 'avaliadora']).exists()
        return obj == request.user

class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
    
class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        roles = {group.name for group in user.groups.all()}
        return 'admin' in roles