from django.http import HttpResponse
from django.template import Template, Context
from django.db.models import Max
from settings import TEMPLATE_DIRS
from mombabyprods.models import MilkBrand, MilkSeries, MilkProd, MilkTunnel, QueryHandler
from datetime import *

colorset = {
             'tmall' : "255,153,18",
              'jd' : "138,54,15",
              'dangdang' : "112,128,105",
              'yhd' : "50,205,50",
              'suning' : "218,112,214" ,
              'weiwei' : "153,51,250",
              'sfbest' : "255,69,0",
            }

def hello(request):
    return HttpResponse("Hello world")

def brands(request):
    return HttpResponse("\n".join(QueryHandler.Brands()))

def seriesofbrand(request, ebrand):
    brand = QueryHandler.EBrand2Brand[ebrand]
    show_list = QueryHandler.Series(brand)
    return HttpResponse(str(show_list))

def __renderShowList(show_list):
    for item in show_list:
        showdict = []
        showdict['seriesName'] = item.name
        showdict['title'] = '200 yuan, 900g'
        showdict['picurl'] = item.pic_link
        showdict['url'] = u"http://%s/series/%s/trend" % ('10.31.186.63', item.ename)
 
def trendofseries(request, series):
    data = QueryHandler.TrendDataOfSeries(series, 10, 3)
    return RenderBrandCharts(data)

def trendofbrand(request, brand):
    data = QueryHandler.TrendDataOfBrand(u'\u60e0\u6c0f', 10, 3)
    html = RenderBrandCharts(data)
    return HttpResponse(html)   

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
    



