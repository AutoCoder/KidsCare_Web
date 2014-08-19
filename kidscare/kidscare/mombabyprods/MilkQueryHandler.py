import MySQLdb
import datetime
from kidscare.settings import DbHost
from models import MilkBrand, MilkProd, MilkSeries, MilkTunnel


def connectdb():
    try:
        conn = MySQLdb.connect(host=DbHost, user='spider',passwd='wodemima',port=3306, charset='utf8')
        conn.select_db('Mom_Baby')
        return conn
    except:
        assert(False)
        
Dbconnection = connectdb()
        
def DbConn():
    global Dbconnection
    try:
        Dbconnection.ping()
    except Exception,info:
        print "%s" % info
        Dbconnection = connectdb()
    
    return Dbconnection

class QueryHandler(object):
    Tunnels2Ltunnels = {}
    Series2ESeries = {}
    ESeries2Series = {}
    EBrand2Brand = {}; Brand2EBrand = {};
    for item in MilkBrand.objects.all():
        EBrand2Brand[item.ename] = item.name
        Brand2EBrand[item.name] = item.ename
    for item in MilkTunnel.objects.all():
        Tunnels2Ltunnels[item.name] = item.cname
    for item in MilkSeries.objects.all():
        Series2ESeries[item.name] = item.ename
        ESeries2Series[item.ename] = item.name
    
    @staticmethod
    def Brands():
        return [item.name for item in MilkBrand.objects.all()]
    
    @staticmethod
    def BrandName(series):
        brandset = MilkSeries.objects.filter(name=series)
        if brandset:
            return brandset[0].brandin
        else:
            return None

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
            for tunnelstr in QueryHandler.Tunnels2Ltunnels.keys():
                count = MilkProd.objects.filter(name=seriesname, tunnel=tunnelstr).count()
                if count:
                    temp = MilkProd.objects.filter(name=seriesname, tunnel=tunnelstr).order_by('-scrapy_time')[0]
                    if temp and cheapest.unitprice > temp.unitprice:
                        cheapest = temp
            cheapest_prod.append(cheapest)
        return cheapest_prod
    
    @staticmethod
    def getLatestprods(series, tunnelName, seg):
        now = datetime.datetime.now()
        start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
        count = MilkProd.objects.filter(name=series, tunnel=tunnelName, segment=seg, scrapy_time__gt=start).count()
        if count:
            return MilkProd.objects.filter(name=series, tunnel=tunnelName, segment=seg, scrapy_time__gt=start).order_by('unitprice')[0]
        else:
            return None 
    
    @staticmethod
    def GetTrendData(ser, segment, tunnel, duration, interval):# (duration , interval) unit = day
        """we need to select by the series from here"""
        try:
            #QueryHandler.conn.select_db('Mom_Baby')
            subsection = int(duration / interval)
            cur = DbConn().cursor()
            sql = u"""Select tunnel, brand, segment, name, price, unitprice, volume, pic_link, prod_link, scrapy_time FROM
                    (SELECT tunnel, brand, segment, name, price, unitprice, volume, pic_link, prod_link, scrapy_time,
                    timestampdiff (hour, scrapy_time, NOW()) AS intervals 
                    FROM mom_baby.milk_prod where segment = %d and name = '%s' and tunnel = '%s' and scrapy_time between date_sub(NOW(), INTERVAL %d DAY) and NOW()
                    ) AS t 
                    WHERE (t.intervals %s) < 24
                        order by scrapy_time Asc;""" % (segment, ser, tunnel, duration, '% ' + str(subsection * 24))
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
                branddict[series.name] = QueryHandler.TrendDataOfSeries(series.name, duration, interval)
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
            for tunnel in QueryHandler.Tunnels2Ltunnels.keys():
                tunneldict[tunnel] = QueryHandler.GetTrendData(series, seg, tunnel, duration, interval)
            segdict[seg] = tunneldict
        return segdict                #QueryHandler.GetTrendData(series, duration, interval)
