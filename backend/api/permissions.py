from rest_framework import permissions


class AllowAllOrIsAuthenticated(permissions.BasePermission):
    """
    Пользовательский класс разрешений, дает доступ к определенным действиям
    в зависимости от авторизации пользователя.
    """
    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение указанного действия.
        """
        if view.action == 'me':
            return request.user.is_authenticated
        return True


class IsRecipeAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательский класс разрешений, ограничивающий доступ к рецептам в
    зависимости от авторства.
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение указанного действия над объектом.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
