from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user