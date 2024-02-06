from rest_framework import permissions

from restaurant_app.models import MenuItem, Restaurant

class IsAdminOfRestaurant(permissions.BasePermission):
   
    def has_object_permission(self, request, view, obj):
        # Check if the admin is associated with the restaurant or menu item
        if isinstance(obj, Restaurant):
            return obj.admin.user == request.user
        elif isinstance(obj, MenuItem):
            return obj.restaurant.admin.user == request.user

    def has_permission(self, request, view):
        if request.method == 'POST':
            # Check if the user is a restaurant owner and the restaurant matches
            restaurant_id = request.data.get('restaurant_id')
            if restaurant_id:
                restaurant = Restaurant.objects.get(pk=restaurant_id)
                return request.user.role == 'restaurant_owner' and restaurant.admin.user == request.user
        elif request.method == 'DELETE':
            # Check if the user has permission to delete the specific object
            obj = view.get_object()
            return self.has_object_permission(request, view, obj)
        
        return request.user.role == 'restaurant_owner'