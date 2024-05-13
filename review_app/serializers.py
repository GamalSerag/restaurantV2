from rest_framework import serializers
from .models import QualityRating, DeliveryRating
from django.core.validators import MinValueValidator, MaxValueValidator


class QualityRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityRating
        fields = ['id', 'order', 'customer', 'rating', 'comment']


class DeliveryRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRating
        fields = ['id', 'order', 'customer', 'rating']


class CombinedRatingSerializer(serializers.Serializer):
    quality_rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    delivery_rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = serializers.CharField(allow_blank=True)



class OrderRatingSerializer(serializers.ModelSerializer):
    quality_rating = serializers.FloatField(source='quality.rating', read_only=True)
    delivery_rating = serializers.FloatField(source='delivery.rating', read_only=True)

    class Meta:
        model = QualityRating  # You can use DeliveryRating if needed
        fields = ['id', 'order', 'quality_rating', 'delivery_rating', 'comment']

class RestaurantRatingsSerializer(serializers.Serializer):
    total_rating = serializers.FloatField()
    rating_count = serializers.IntegerField()
    rates = serializers.ListField(child=serializers.DictField())