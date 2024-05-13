from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order, QualityRating, DeliveryRating, TotalRating
from .serializers import OrderRatingSerializer, QualityRatingSerializer, DeliveryRatingSerializer, CombinedRatingSerializer, RestaurantRatingsSerializer
from django.db.models import Avg, Count

class CombinedRatingView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        combined_serializer = CombinedRatingSerializer(data=request.data)
        customer = request.user.customer_profile
        if combined_serializer.is_valid():
            try:
                order_id = request.data['order_id']
            except KeyError:
                return Response({"message": "Order ID not provided, ensure it is an integer and the key is order_id."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if ratings already exist for the order
            if QualityRating.objects.filter(order=order, customer=customer).exists() or \
                    DeliveryRating.objects.filter(order=order, customer=customer).exists():
                return Response({"message": "Order has already been rated."}, status=status.HTTP_400_BAD_REQUEST)

            quality_serializer = QualityRatingSerializer(data={
                'order': order_id,
                'customer': customer.id,
                'rating': combined_serializer.validated_data['quality_rating'],
                'comment': request.data.get('comment')  # Assuming 'quality_comment' is sent in the request data
            })
            delivery_serializer = DeliveryRatingSerializer(data={
                'order': order_id,
                'customer': customer.id,
                'rating': combined_serializer.validated_data['delivery_rating'],
            })
            if quality_serializer.is_valid() and delivery_serializer.is_valid():
                quality_serializer.save()
                delivery_serializer.save()

                # Get the restaurant related to the order
                restaurant = order.restaurant

                # Update total rating for the restaurant
                total_rating, created = TotalRating.objects.get_or_create(restaurant=restaurant)
                total_rating.calculate_total_rating()

                return Response({"message": "Ratings submitted successfully."}, status=status.HTTP_201_CREATED)
            else:
                errors = {}
                if not quality_serializer.is_valid():
                    errors['quality_rating'] = quality_serializer.errors
                if not delivery_serializer.is_valid():
                    errors['delivery_rating'] = delivery_serializer.errors
                return Response({"message": "Invalid data for quality or delivery rating.", "errors": errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Invalid data for combined rating.", "errors": combined_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)




class RetrieveRatingsView(generics.RetrieveAPIView):
    serializer_class = CombinedRatingSerializer

    def get_queryset(self):
        user = self.request.user
        order_id = self.kwargs.get('order_id')
        return QualityRating.objects.filter(customer=user, order_id=order_id), \
              DeliveryRating.objects.filter(customer=user, order_id=order_id)

    def get(self, request, *args, **kwargs):
        quality_ratings, delivery_ratings = self.get_queryset()

        if not quality_ratings.exists() or not delivery_ratings.exists():
            return Response({"message": "Ratings not found for the specified user and order."},
                            status=status.HTTP_404_NOT_FOUND)

        

        combined_ratings = {
            'quality_rating': quality_ratings.first.rating,
            'delivery_rating': delivery_ratings.first.rating,
            'comment': quality_ratings.first().comment if quality_ratings.exists() else '',
        }

        serializer = self.get_serializer(data=combined_ratings)
        serializer.is_valid()

        return Response(serializer.data)
    



class RestaurantRatingsView(generics.RetrieveAPIView):
    serializer_class = RestaurantRatingsSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        quality_ratings = QualityRating.objects.filter(order__restaurant_id=restaurant_id)
        delivery_ratings = DeliveryRating.objects.filter(order__restaurant_id=restaurant_id)
        total_rating_obj = TotalRating.objects.filter(restaurant_id=restaurant_id).first()

        return quality_ratings, delivery_ratings, total_rating_obj

    def retrieve(self, request, *args, **kwargs):
        quality_ratings, delivery_ratings, total_rating_obj = self.get_queryset()

        ratings_data = []
        for quality_rating in quality_ratings:
            delivery_rating = delivery_ratings.filter(order=quality_rating.order).first()
            if delivery_rating:
                rating_data = {
                    'created_at': quality_rating.created_at,
                    'user_name': f'{quality_rating.customer.first_name} {quality_rating.customer.last_name}',
                    'order_id': quality_rating.order.id,
                    'quality_rating': quality_rating.rating,
                    'delivery_rating': delivery_rating.rating,
                    'comment': quality_rating.comment if quality_rating.comment else '',
                }
                ratings_data.append(rating_data)

        total_rating = total_rating_obj.total_rating if total_rating_obj else 0
        rating_count = quality_ratings.count() if quality_ratings else 0

        response_data = {

            'total_rating': total_rating,
            'rating_count': rating_count,
            'rates': ratings_data,
        }

        serializer = self.get_serializer(response_data)
        return Response(serializer.data)

