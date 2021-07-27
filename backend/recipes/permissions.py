from rest_framework import permissions


class CurrentUserOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        if type(obj.author) == type(user) and obj.author == user:
            return True
        return request.method in permissions.SAFE_METHODS or user.is_staff
