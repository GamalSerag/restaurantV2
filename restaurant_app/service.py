from django.db.models import Count


def apply_restaurants_filters( queryset,  params):
        
        ''' 
        This function filters the queryset based on the params passed in the request 
        params = {
            'type': 'restaurant' or 'menu_item',
            'availability': 'open' or 'closed',
            'freeDelivery': 'true' or 'false',
            'minOrderAmount': 0,
            'rating': 0,
            'orderBy': 'rating, popularity, deliveryFee, or minimumOrderValue'
            'hasOffer': 'true' or 'false'

        }

        '''

        print(params)
        search_type = params.get('type', 'restaurant').lower()
        print(search_type)
        state = params.get('availability')
        free_delivery = params.get('freeDelivery')
        min_order = params.get('minOrderAmount')
        rating = params.get('rating')
        order_by = params.get('orderBy')
        has_offer = params.get('hasOffer')

        if state:
            state_filter = {'restaurant__state': state.capitalize()} if search_type == 'menu_item' else {'state': state.capitalize()}
            queryset = queryset.filter(**state_filter)
        if free_delivery:
            free_delivery = free_delivery.lower() == 'true'
            free_delivery_filter = {'restaurant__free_delivery': free_delivery} if search_type == 'menu_item' else {'free_delivery': free_delivery}
            queryset = queryset.filter(**free_delivery_filter)
        if min_order:
            min_order_filter = {'restaurant__minimum_order__lte': min_order} if search_type == 'menu_item' else {'minimum_order__lte': min_order}
            queryset = queryset.filter(**min_order_filter)
        if rating:
            rating = float(rating)
            rating_filter = {'restaurant__totalrating__total_rating__lte': rating} if search_type == 'menu_item' else {'totalrating__total_rating__lte': rating}
            queryset = queryset.filter(**rating_filter)
        if order_by:
            if order_by == 'rating':
                queryset = queryset.order_by('-totalrating__total_rating')
            elif order_by == 'popularity':
                # Annotate the queryset with the count of orders for each restaurant
                queryset = queryset.annotate(num_orders=Count('order'))
                # Order by the count of orders in descending order (most popular first)
                queryset = queryset.order_by('-num_orders')
                for restaurant in queryset:
                    print(f'Restaurant: {restaurant.name}, Orders: {restaurant.num_orders}')

            elif order_by == 'deliveryFee':
                queryset = queryset.order_by('delivery_fee')

            elif order_by == 'minimumOrderValue':
                queryset = queryset.order_by('minimum_order')
        if has_offer:
            has_offer_bool = has_offer.lower() == 'true'
            if search_type == 'menu_item':
                offer_filter = {'offer__isnull': False} if has_offer_bool else {'offer__isnull': True}
            else:
                offer_filter = {'menuitem__offer__isnull': False} if has_offer_bool else {'menuitem__offer__isnull': True}
            queryset = queryset.filter(**offer_filter).distinct()

        return queryset