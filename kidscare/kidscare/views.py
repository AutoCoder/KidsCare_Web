from django.http import HttpResponse
from django.template import Template, Context
from settings import TEMPLATE_DIRS
from mombabyprods.models import MilkBrand, MilkSeries, MilkProd

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

class QueryHandler(object):
    
    @staticmethod
    def Brands():
        return [item.name for item in MilkBrand.objects.all()]

    @staticmethod
    def Series(brand=''):
        if not brand:
            return [item.name for item in MilkSeries.objects().filter(BrandIn=brand)]
        else:
            return [item.name for item in MilkSeries.objects().all()]
    
    @staticmethod
    def TrendDataCollection(brand="", series="", duration, interval=1):
        """
        @brand, user input brand for search & price compare
        @series, user input series for search & price compare
        @duration, price chart duration, for example from 2014-07-21 to 2014-08-21 30 days
        @interval, price chart x-coordinate interval. for example. if duration = 30day, interval = 3day, this function will return a list contain 10 elements
        """
        def TrendDataCollection(ser="", duration, interval=1):
            """we need to select by the series from here"""
            pass
        
        if brand not in QueryHandler.Brands():
            if series not in QueryHandler.Series():
                return [] #return empty trend data
            else:
                TrendDataCollection(series, duration, interval)
        else:
            if series not in QueryHandler.Series(brand):
                pass # ignore the series input
            else:
                TrendDataCollection(series, duration, interval)
