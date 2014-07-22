# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class MilkProd(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True) # Field name made lowercase.
    tunnel = models.CharField(max_length=20, blank=True)
    brand = models.TextField(blank=True)
    name = models.TextField(blank=True)
    segment = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    unitprice = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    packaging_type = models.CharField(max_length=8, blank=True)
    pic_link = models.TextField(blank=True)
    prod_link = models.TextField(blank=True)
    scrapy_time = models.DateTimeField(primary_key=True)
    class Meta:
        managed = False 
        db_table = 'milk_prod'

class MilkBrand(models.Model):
    name = models.TextField(blank=False)
    
class MilkSeries(models.Model):
    name = models.TextField(blank=False)
    BrandIn = models.TextField(blank=False)