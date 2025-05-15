from rest_framework.permissions import BasePermission, SAFE_METHODS

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