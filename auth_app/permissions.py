from rest_framework import permissions

class IsAdminOfRestaurant(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an admin
        return request.user.role == 'restaurant_owner'

    def has_object_permission(self, request, view, obj):
        # Check if the admin is associated with the restaurant
        return obj.admin.user == request.user