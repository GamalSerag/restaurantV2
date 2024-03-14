from django.db import models


def country_logo_path(instance, filename):
    country_name = instance.name
    country_name = country_name.replace(' ', '_').lower()
    return f'country/logo/{country_name}/{filename}'


class Country(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=country_logo_path, null=True)

    def __str__(self):
        return self.name

class City(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.name}, {self.country.name}"
