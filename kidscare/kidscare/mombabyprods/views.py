from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context

from MilkQueryHandler import QueryHandler
from kidscare.settings import TEMPLATE_DIR
from kidscare.Profiler import profile
from WeiXinHandler import WeiXinHandler

# Create your views here.
colorset = {
             'tmall' : "255,153,18",
              'jd' : "138,54,15",
              'dangdang' : "112,128,105",
              'yhd' : "50,205,50",
              'suning' : "218,112,214" ,
              'weiwei' : "153,51,250",
              'sfbest' : "255,69,0",
            }

def handleWXHttpRequest(request):
    if request.method == 'GET':
        return HttpResponse(WeiXinHandler.checkSignature(request))
    elif request.method == 'POST':
        return HttpResponse(WeiXinHandler.response_msg(request))
    
#@profile("1000.prof")
def seriesofbrand(request, ebrand, brand=None, msg={'ToUserName':'lilei', 'FromUserName':'hanmeimei'}):
    branda = brand if brand else QueryHandler.EBrand2Brand[ebrand] 
    return HttpResponse(WeiXinHandler.reponse_seriescharts(branda, msg))
       
#@profile("2000.prof") 
def trendofseries(request, series):
    data = QueryHandler.TrendDataOfSeries(QueryHandler.ESeries2Series[series], 10, 3)
    html =  RenderSeriesCharts(data, series)
    return HttpResponse(html)   

def trendofbrand(request, ebrand):
    brandc = QueryHandler.EBrand2Brand[ebrand] 
    data = QueryHandler.TrendDataOfBrand(brandc, 10, 3)
    html = RenderBrandCharts(data, brandc)
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

def RenderBrandCharts(dictdata, brand):
    fp = open(TEMPLATE_DIR + '/chart_templ')
    t = Template(fp.read())
    fp.close()
    #dict = { "S-26" : { 1:{ 'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 2:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 3:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 4:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}} } 

    chartdata_list = preprocessTrendData(dictdata)
    c = Context({
                 'brand_passed' : True,
                 'brand' : brand,
                 'series_list': dictdata.items(),
                 'chartdata_list': chartdata_list,
                 'realchartIds' : [ (item[0], item[0].replace('_','-')) for item in chartdata_list ]
                 })
    html = t.render(c)
    return html
    
def RenderSeriesCharts(dictdata, series):
    fp = open(TEMPLATE_DIR + '/chart_templ')
    t = Template(fp.read())
    fp.close()
    #dict = { "S-26" : { 1:{ 'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 2:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 3:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 4:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}} } 

    def preprocess_dictdata():
        """
        preprocess dictdata to remove the empty dict node(segment)
        """
        for segKey,segValue in dictdata.items():
            isremovable = True
            for tunnelKey,tunnelValue in segValue.items():
                if tunnelValue:
                    isremovable = False
                    break
            if isremovable:
                del dictdata[segKey]
                
    preprocess_dictdata()
    series_zh = QueryHandler.ESeries2Series[series]
    brandname = QueryHandler.BrandName(series_zh)   
    if brandname:
        page_title = "%s -> %s" % (brandname, series_zh)
    else:
        page_title = "%s" % (series_zh)
                               
    origDict = {}
    origDict[series_zh] = dictdata
    chartdata_list = preprocessTrendData(origDict)
    c = Context({
                 'page_title' : page_title,
                 'brand' : brandname,
                 'series_list': origDict.items(),
                 'chartdata_list': chartdata_list,
                 'realchartIds' : [ (item[0], item[0].replace('_','-')) for item in chartdata_list ]
                 })
    return t.render(c)