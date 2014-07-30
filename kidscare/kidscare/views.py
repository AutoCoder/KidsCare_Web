from django.http import HttpResponse
from django.template import Template, Context
from settings import TEMPLATE_DIRS
from mombabyprods.models import MilkBrand, MilkSeries, MilkProd
import MySQLdb
import platform
from datetime import *

Tunnels = ["tmall", "jd", "dangdang", "yhd", "suning", "weiwei", "sfbest"]
colorset = {
             'tmall' : "255,153,18",
              'jd' : "138,54,15",
              'dangdang' : "112,128,105",
              'yhd' : "50,205,50",
              'suning' : "218,112,214" ,
              'weiwei' : "153,51,250",
              'sfbest' : "255,69,0",
            }
DbHost = None
if platform.system() is 'Windows':
    DbHost = '127.0.0.1'
elif platform.system() in ('Linux',):
    DbHost = '10.31.186.63'
else:
    DbHost = '10.31.186.63'
    
def hello(request):
    return HttpResponse("Hello world")

def price_chart(request):
    fp = open(TEMPLATE_DIRS[0] + '/chart_templ')
    t = Template(fp.read())
    fp.close()
    html = t.render(Context({'title': u"\u5317\u4eac\u002d\u9999\u6e2f",
    	'detail_link' : 'http://touch.dujia.qunar.com/pi/detail_736558137',
    	'label_list' : ['2014-07-01', '2014-07-02', '2014-07-03', '2014-07-04', '2014-07-05', '2014-07-06', '2014-07-07'],
    	'price_list' : [2000, 1000, 3000, 2500, 1500, 2000, 1500]}
    	))
    return HttpResponse(html)

def brands(request):
    return HttpResponse("\n".join(QueryHandler.Brands()))

def Series(request):
    return HttpResponse("\n".join(QueryHandler.Series(u'\u60e0\u6c0f')))
   
def preprocessTrendData(dictdata):
    chartdata_list = []
    for seriesName,seriesData in dictdata.items():
        for seg, chartdata in seriesData.items():
            chartid = (u"%s_%d" % (seriesName, seg)).replace('-','_')
            chartdatatempl = """{labels : %s, datasets : [ %s ]}"""
            #list all scrapy date(unique) 
            labels = []
            tunneldictlist = {}
            for tunnel, tunneldata in chartdata.items():
                date2price = {}
                if len(tunneldata):
                    tunneldictlist[tunnel] = [0]
                else:
                    continue
                for item in tunneldata:
                    date2price[item[9].date()] = item[5]
                labels += date2price.keys()
            labels = sorted({}.fromkeys(labels).keys())
            labelStrList = [ label.strftime('%Y-%m-%d') for label in labels]
            
            #fill the array with 0 value at initial
            axis_size = len(labels)
            for tunnel in tunneldictlist.keys():
                tunneldictlist[tunnel] *= axis_size
              
            linkdict = {}
            for tunnel, tunneldata in chartdata.items():
                for item in tunneldata:
                    idx = labels.index(item[9].date())
                    tunneldictlist[tunnel][idx] = item[5]
                    linkdict[tunnel] = item[8]
                    
            for tunnel, trenddata in tunneldictlist.items():
                i = 0 
                while trenddata[i] == 0:
                    i+=1
                fillval = trenddata[i]
                for i in xrange(len(trenddata)):
                    if trenddata[i] is 0:
                        trenddata[i] = fillval
                    else:
                        fillval = trenddata[i]
                        
            tempstr = """{label: "%s", fillColor : "rgba(%s,0.2)", strokeColor : "rgba(%s,1)", pointColor : "rgba(%s,1)", pointStrokeColor : "#fff", pointHighlightFill : "#fff", pointHighlightStroke : "rgba(%s,1)", prodlink : "%s", data : %s},"""
            datasetsStr = ''
            for tunnel, trenddata in tunneldictlist.items():
                datasetsStr += tempstr % (tunnel, colorset[tunnel], colorset[tunnel], colorset[tunnel], colorset[tunnel], linkdict[tunnel], trenddata)
                
            chartdata = chartdatatempl % (labelStrList, datasetsStr)
            chartdata_list.append((chartid, chartdata))
            
    return chartdata_list

def RenderBrandCharts(dictdata):
    fp = open(TEMPLATE_DIRS[0] + '/chart_templ')
    t = Template(fp.read())
    fp.close()
    #dict = { "S-26" : { 1:{ 'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 2:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 3:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 4:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}} } 

    chartdata_list = preprocessTrendData(dictdata)
    c = Context({
                 'brand_passed' : False,
                 'series_list': dictdata.items(),
                 'chartdata_list': chartdata_list,
                 'realchartIds' : [ (item[0], item[0].replace('_','-')) for item in chartdata_list ]
                 })
    html = t.render(c)
    return html
    
def trendofbrand(request, brand):
    conn = MySQLdb.connect(host=DbHost, user='spider',passwd='wodemima',port=3306, charset='utf8')
    conn.select_db('Mom_Baby')
    data = QueryHandler.TrendDataOfBrand(conn, u'\u60e0\u6c0f', 10, 3)
    html = RenderBrandCharts(data)
    return HttpResponse(html)

def trendofseries(request, series):
    conn = MySQLdb.connect(host=DbHost, user='spider',passwd='wodemima',port=3306, charset='utf8')
    conn.select_db('Mom_Baby')
    data = QueryHandler.TrendDataOfSeries(conn, series, 10, 3)
    #return HttpResponse(str(t))
    return RenderBrandCharts(data)

class QueryHandler(object):
    #conn = MySQLdb.connect(host=DbHost, user='spider',passwd='wodemima',port=3306, charset='utf8')
    
    @staticmethod
    def Brands():
        return [item.name for item in MilkBrand.objects.all()]

    @staticmethod
    def Series(brand=''):
        if brand:
            return [item.name for item in MilkSeries.objects.filter(BrandIn=brand)]
        else:
            return [item.name for item in MilkSeries.objects.all()]
        
    @staticmethod
    def GetTrendData(conn, ser, segment, tunnel, duration, interval):# (duration , interval) unit = day
        """we need to select by the series from here"""
        try:
            #QueryHandler.conn.select_db('Mom_Baby')
            subsection = int(duration / interval)
            cur = conn.cursor()
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
    def TrendDataOfBrand(conn, brand, duration, interval):
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
                branddict[series] = QueryHandler.TrendDataOfSeries(conn, series, duration, interval)
            return branddict
        
    @staticmethod
    def TrendDataOfSeries(conn, series, duration, interval):
        """
        @series, user input series for search & price compare
        @duration, price chart duration, for example from 2014-07-21 to 2014-08-21 30 days
        @interval, price chart x-coordinate interval. for example. if duration = 30day, interval = 3day, this function will return a list contain 10 elements
        """
        segdict = {}
        for seg in xrange(1, 5):
            tunneldict = {}
            for tunnel in Tunnels:
                tunneldict[tunnel] = QueryHandler.GetTrendData(conn, series, seg, tunnel, duration, interval)
            segdict[seg] = tunneldict
        return segdict                #QueryHandler.GetTrendData(series, duration, interval)
