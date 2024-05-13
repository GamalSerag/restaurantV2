from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

from django.http import Http404
def calculate_cart_item_total_prices(menu_item, selected_type_ids, selected_extra_ids, quantity):
    from .models import MenuItemTypeItem, MenuItemExtraItem
    try:
        size_and_price_obj = menu_item.sizeandprice_set.first()
        base_price = Decimal(size_and_price_obj.price)

        total_price_with_quantity = base_price * quantity
        total_price_without_quantity = base_price

        if selected_type_ids:
            for selected_type_id in selected_type_ids:
                try:
                    selected_type_price = Decimal(MenuItemTypeItem.objects.get(id=selected_type_id).price)
                    total_price_with_quantity += selected_type_price * quantity
                    total_price_without_quantity += selected_type_price
                except ObjectDoesNotExist:
                    pass

        if selected_extra_ids:
            for selected_extra_id in selected_extra_ids:
                try:
                    selected_extra_price = Decimal(MenuItemExtraItem.objects.get(id=selected_extra_id).price)
                    total_price_with_quantity += selected_extra_price * quantity
                    total_price_without_quantity += selected_extra_price
                except ObjectDoesNotExist:
                    pass

        return base_price, total_price_with_quantity, total_price_without_quantity

    except ObjectDoesNotExist:
        raise Http404({"Error": "SizeAndPrice for menu item does not exist"})
