from django.db import models
from restaurant_app.models import Restaurant, RestaurantRegion


class Employee(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    national_number = models.CharField(max_length=255)
    region = models.ForeignKey(RestaurantRegion, on_delete=models.CASCADE)
    restaurant_section = models.CharField(max_length=255, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Shift(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Shift #{self.pk} - {self.restaurant.name}"



class EmployeePerformance(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    evaluation_date = models.DateField()       ####$$$    ?   $$$#####
    rate = models.IntegerField()     ####$$$    ?   $$$#####
    evaluation_type = models.CharField(max_length=255)      ####$$$    ?   $$$#####
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Performance #{self.pk} - {self.employee.first_name} {self.employee.last_name}"

