from rest_framework import permissions


class AllowAllOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return True


class IsRecipeAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user