from rest_framework import serializers

from restaurant_app.serializers import RestaurantSerializer
from .models import Admin, AdminAdress, AdminDoc
from auth_app.serializers import UserSerializer
from restaurant_app.models import Restaurant
from drf_writable_nested.serializers import WritableNestedModelSerializer

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    restaurant_name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = ['id', 'user', 'phone_number', 'created_at', 'first_name', 'last_name', 'restaurant', 'restaurant_name', 'subscription', 'is_subscribed', 'is_approved']

    def get_restaurant_name(self, obj):
        if obj.restaurant:
            return obj.restaurant.name
        return None
    
    def get_subscription(self, obj):
        if obj.restaurant:
            subscription = obj.subscription
            if subscription:
                return {'id': subscription.id , 'name': subscription.name, 'price': subscription.price, 'commission_rate': subscription.commission_rate, 'duration': subscription.duration }
        return None




class AdminAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAdress
        fields = ['line1', 'postal_code', 'city']


class AdminDocSerializer(serializers.ModelSerializer):
    address = AdminAddressSerializer()

    class Meta:
        model = AdminDoc
        fields = ['leagal_name','phone', 'ID_photo', 'business_register', 'address']

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = AdminAdress.objects.create(**address_data)
        admin_doc = AdminDoc.objects.create(address=address, **validated_data)
        return admin_doc
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address_instance = instance.address
            address_serializer = AdminAddressSerializer(address_instance, data=address_data, partial=True)
            if address_serializer.is_valid():
                address_serializer.save()
            else:
                # Handle validation errors for address fields
                raise serializers.ValidationError(address_serializer.errors)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    



class AdminListSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    email = serializers.SerializerMethodField()
    admin_docs = AdminDocSerializer(many=True)
    subscription = serializers.SerializerMethodField()
    # restaurant = RestaurantSerializer(many=True)

    class Meta:
        model = Admin
        fields = ['id','first_name', 'last_name',  'email' ,  'phone_number', 'created_at', 
                  'restaurant', 'subscription', 'is_subscribed', 'is_approved','is_rejected', 'has_submitted_docs', 'admin_docs']
        

    def get_subscription(self, obj):
        if obj.restaurant:
            subscription = obj.subscription
            if subscription:
                return {'id': subscription.id , 'name': subscription.name, 'price': subscription.price, 'commission_rate': subscription.commission_rate, 'duration': subscription.duration }
        return None
    
    def get_email(self, obj):
        return obj.user.email
    
class AdminDetailForSuperAdminSerializer(serializers.ModelSerializer):
    
    email = serializers.SerializerMethodField()
    admin_docs = serializers.SerializerMethodField()
    restaurant_latitude = serializers.SerializerMethodField()
    restaurant_lngitude = serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'created_at', 
                'restaurant', 'subscription', 'is_subscribed', 'is_approved' ,'is_rejected' , 'has_submitted_docs', 'admin_docs', 'restaurant_latitude', 'restaurant_lngitude']

    def get_admin_docs(self, obj):
        admin_docs = AdminDoc.objects.filter(admin=obj).all()
        if admin_docs:
            serializer = AdminDocSerializer(admin_docs, many=True)
            # Update file URLs to include the media URL for each document
            data = serializer.data
            for doc_data in data:
                doc_data['ID_photo'] = self.context['request'].build_absolute_uri(doc_data['ID_photo'])
                doc_data['business_register'] = self.context['request'].build_absolute_uri(doc_data['business_register'])
            return data
        return None
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_restaurant_latitude(self, obj):
        if obj.restaurant:
            return obj.restaurant.latitude
        
        return None
    
    def get_restaurant_lngitude(self, obj):
        if obj.restaurant:
            return obj.restaurant.longitude
        
        return None
    


    
    # def get_restaurant(self, obj):
    
    #     restaurant_name = obj.name
    #     if restaurant_name:
    #         return {'name': restaurant_name }
    #     return None
    


