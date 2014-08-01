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
import MySQLdb
import platform

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'

class MilkBrand(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    ename = models.TextField()
    class Meta:
        managed = False
        db_table = 'milk_brand'

class MilkProd(models.Model):
    id = models.IntegerField(db_column='Id',primary_key=True) # Field name made lowercase.
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
    scrapy_time = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'milk_prod'

class MilkSeries(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    brandin = models.TextField(db_column='BrandIn') # Field name made lowercase.
    ename = models.TextField()
    ebrandin = models.TextField(db_column='eBrandIn') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'milk_series'

class MilkTunnel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    class Meta:
        managed = False
        db_table = 'milk_tunnel'

Tunnels = ["tmall", "jd", "dangdang", "yhd", "suning", "weiwei", "sfbest"]

DbHost = None
if platform.system() is 'Windows':
    DbHost = '127.0.0.1'
elif platform.system() in ('Linux',):
    DbHost = '10.31.186.63'
else:
    DbHost = '10.31.186.63'
DbConn = MySQLdb.connect(host=DbHost, user='spider',passwd='wodemima',port=3306, charset='utf8')
DbConn.select_db('Mom_Baby')   

class QueryHandler(object):
    tunnels = [item.name for item in MilkTunnel.objects.all()]
    EBrand2Brand = {}; Brand2EBrand = {};
    for item in MilkBrand.objects.all():
        EBrand2Brand[item.ename] = item.name
        Brand2EBrand[item.name] = item.ename
    
    @staticmethod
    def Brands():
        return [item.name for item in MilkBrand.objects.all()]

    @staticmethod
    def Series(brand):
        series_list = []
        if brand:
            series_list = [item.name for item in MilkSeries.objects.filter(brandin=brand)]
        else:
            return []
        
        cheapest_prod = []
        for seriesname in series_list:
            cheapest = MilkProd(unitprice=10000)
            for tunnelstr in QueryHandler.tunnels:
                temp = MilkProd.objects.filter(name=seriesname, tunnel=tunnelstr).order_by('-scrapy_time')
                if temp and cheapest.unitprice > temp[0].unitprice:
                    cheapest = temp[0]
            cheapest_prod.append(cheapest)
        return cheapest_prod
    
    @staticmethod
    def GetTrendData(ser, segment, tunnel, duration, interval):# (duration , interval) unit = day
        """we need to select by the series from here"""
        try:
            #QueryHandler.conn.select_db('Mom_Baby')
            subsection = int(duration / interval)
            cur = DbConn.cursor()
            sql = u"""Select tunnel, brand, segment, name, price, unitprice, volume, pic_link, prod_link, scrapy_time FROM
                    (SELECT tunnel, brand, segment, name, price, unitprice, volume, pic_link, prod_link, scrapy_time,
                    timestampdiff (hour, scrapy_time, NOW()) AS intervals 
                    FROM mom_baby.milk_prod
                    ) AS t 
                    WHERE (t.intervals %s) < 24 and 
                        tunnel = '%s' and 
                        segment = %d and 
                        name = '%s' and 
                        scrapy_time between date_sub(NOW(), INTERVAL %d DAY) and NOW()
                        order by scrapy_time Asc;""" % ('% ' + str(subsection * 24), tunnel, segment, ser, duration)
            cur.execute(sql)
            rows = cur.fetchall()
        except Exception, e:
                print "Get TrendDataCollection(series=%s, segment=%d, tunnel=%s, duration=%d, interval=%d) failed due to [%s]" % (ser, segment, tunnel, duration, interval, e)
                return {}
        
        def NormalizeTrendData():
            """filter out the non-lowest data in the same date"""
            lowestprice_date = {}
            for item in rows:
                date_key = item[9].date()
                if date_key not in lowestprice_date.keys():
                    lowestprice_date[date_key] = item
                else:
                    if item[5] < lowestprice_date[date_key][5]:
                        lowestprice_date[date_key] = item
            trendlist = lowestprice_date.values()
            trendlist.sort(cmp=lambda x,y:cmp(x[9],y[9]))
            return trendlist
                      
        return NormalizeTrendData();
    
    @staticmethod
    def TrendDataOfBrand(brand, duration, interval):
        """
        @brand, user input brand for search & price compare
        @duration, price chart duration, for example from 2014-07-21 to 2014-08-21 30 days
        @interval, price chart x-coordinate interval. for example. if duration = 30day, interval = 3day, this function will return a list contain 10 elements
        
        this function will list all trend data of all series of brand
        """
        
        if brand not in QueryHandler.Brands():
            return {} #return empty trend data
        else:
            branddict = {}
            for series in QueryHandler.Series(brand):
                branddict[series] = QueryHandler.TrendDataOfSeries(series, duration, interval)
            return branddict
        
    @staticmethod
    def TrendDataOfSeries(series, duration, interval):
        """
        @series, user input series for search & price compare
        @duration, price chart duration, for example from 2014-07-21 to 2014-08-21 30 days
        @interval, price chart x-coordinate interval. for example. if duration = 30day, interval = 3day, this function will return a list contain 10 elements
        """
        segdict = {}
        for seg in xrange(1, 5):
            tunneldict = {}
            for tunnel in Tunnels:
                tunneldict[tunnel] = QueryHandler.GetTrendData(series, seg, tunnel, duration, interval)
            segdict[seg] = tunneldict
        return segdict                #QueryHandler.GetTrendData(series, duration, interval)
