import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
import datetime
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django_resized import ResizedImageField

today = datetime.date.today()

class User(AbstractUser):

    city = (
        ('Surat', 'Surat'),
        ('Bharuch', 'Bharuch'),
    )
    is_publisher = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    phone=models.BigIntegerField(default=0,validators=[RegexValidator(regex='\d{10}',message='invalid number',code='invalid_number')])
    address=models.CharField(max_length=100,null=True)
    city=models.CharField(max_length=20,null=True,choices=city)
    logo=ResizedImageField(null=True,upload_to='logo/')

    def __str__(self):
        return str(self.username)


class MapData(models.Model):
    s=(
        ('Available','Available'),
        ('Not Available', 'Not Available'),
)

    a = (
        ('education', 'education'),
        ('electronics', 'electronics'),
        ('garments', 'garments'),
        ('textile', 'textile'),
        ('bollywood', 'bollywood'),
    )

    publisher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    photo = models.ImageField(null=True,upload_to='banner/')
    uploaded_at = models.DateTimeField(null=True,auto_now_add=True)
    status=models.CharField(max_length=20,null=True,choices=s)
    to_date = models.DateField(null=True, default=today)
    height = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    ad_type = models.CharField(max_length=20,null=True, choices=a)
    address = models.CharField(max_length=100,null=True)

    def __str__(self):
        return str(self.publisher)


class BookNow(models.Model):
    a = (
        ('education', 'education'),
        ('electronics', 'electronics'),
        ('garments', 'garments'),
        ('textile', 'textile'),
        ('bollywood', 'bollywood'),
    )
    publisher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True,related_name='publisher')
    customer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True,related_name='customer')
    mapdata = models.ForeignKey(MapData(), on_delete=models.CASCADE, null=True,related_name='banner')
    uploaded_date = models.DateField(null=True,auto_now_add=True)
    from_date= models.DateField(null=True)
    to_date = models.DateField(null=True)
    status = models.CharField(max_length=20,null=True, default='pending')
    pay_status = models.CharField(max_length=20,null=True, default='pending')
    ad_type = models.CharField(max_length=20,null=True, choices=a)
    photo = models.ImageField(null=True, upload_to='banner/')
    days = models.IntegerField(null=True)


    def __str__(self):
        return str(self.publisher)

class location(models.Model):
    city = (
        ('Surat', 'Surat'),
        ('Bharuch', 'Bharuch'),
    )

    place=models.CharField(max_length=100,null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    city=models.CharField(max_length=20,null=True,choices=city)

    def __str__(self):
        return str(self.place)



class Order_Banner(models.Model):
    cus = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    mapdata = models.ForeignKey(MapData(), on_delete=models.CASCADE, null=True)
    banner = models.ForeignKey(BookNow(), on_delete=models.CASCADE, null=True)
    unid = models.CharField(max_length=20, null=True)
    order_date = models.DateField(null=True,auto_now_add=True)
    status = models.CharField(max_length=20,null=True, default='pending')
    pay = models.IntegerField(null=True)
    txnid = models.CharField(max_length=50,null=True)
    banktxnid = models.IntegerField(null=True)
    txndate = models.CharField(max_length=20,null=True)
    orderid = models.CharField(max_length=20, null=True)


    def __str__(self):
        return str(self.cus)



class Save_Banner(models.Model):
    cus = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    banner = models.ForeignKey(MapData(), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.cus)

class Compare_Banner(models.Model):
    cus = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    banner = models.ForeignKey(MapData(), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.cus)

class Rating_Us(models.Model):
    pub = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='pub')
    cus = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='cus')
    pub_rating = models.IntegerField(null=True)
    rate_us = models.IntegerField(null=True)

    def __str__(self):
        return str(self.cus)
