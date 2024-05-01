from django.contrib import admin
from .models import  QualityRating, DeliveryRating, TotalRating

# Register your models here.

admin.site.register(
    QualityRating
)
admin.site.register(
    DeliveryRating
)
admin.site.register(
    TotalRating
)