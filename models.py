from django.db import models
from django.conf import settings
from django.utils import timezone

class ProfileManager(models.Manager):
    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number) 

class Profile(models.Model):
    phone_number = models.CharField(default="", max_length=25, null=False, blank=False, unique=True)

    objects = ProfileManager()

    class Meta:
        unique_together = [
            ['phone_number', ],
        ]
    def natural_key(self):
        return (self.phone_number, )

class PackageManager(models.Manager):
    def get_by_natural_key(self, price, number_hours):
        return self.get(price=price, number_hours=number_hours)


class Package(models.Model):
    price = models.FloatField()
    number_hours = models.PositiveIntegerField()

    objects = PackageManager()
    
    def __str__(self):
        return f"{self.number_hours}H --------> {self.price}FCFA"
    
    def natural_key(self):
        return (self.price, self.number_hours)

    class Meta:
        ordering = ['price', ]
        unique_together = [
            ('price', 'number_hours')
        ]
    


class Subscription(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True)
    in_processing = models.BooleanField(default=False)
    is_traited = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)   
    

    date_of_traitment = models.DateTimeField(null=True)
    date_of_confirmation = models.DateTimeField(null=True)
    date_of_subscription = models.DateTimeField(auto_now_add=True, auto_now=False)


class Transaction(models.Model):
    amount = models.FloatField()
    date = models.DateField(auto_now=False, auto_now_add=False, default=timezone.now)
    uuid_transaction = models.CharField(max_length=25, blank=False, unique=True)


class TokenMessage(models.Model):
    message = models.CharField(max_length=255, default='', blank=False, null=False)
    is_sent = models.BooleanField(default=False)