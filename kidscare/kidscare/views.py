from django.http import HttpResponse
from django.template import Template, Context
from settings import TEMPLATE_DIRS
from mombabyprods.MilkQueryHandler import QueryHandler
from Profiler import profile
import hashlib
import time
import xml.etree.ElementTree as ET

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
        return checkSignature(request)
    elif request.method == 'POST':
        return response_msg(request)

def checkSignature(request):
    token = "gonnatravel"  # TOKEN setted in weixin
    signature = request.GET.get('signature', None)
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return echostr
    else:
        return None   

def response_msg(request):
    recvmsg = request.body # 
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
        
    if msg["MsgType"] == "event":
        echostr = '%s%s%s%s' % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
            u"welcome to subscribe mom_baby")
        return echostr
    else:
        #only support milk_brand input
        brand_input = msg["Content"]#.encode("utf-8")
        if brand_input in QueryHandler.Brand2EBrand.keys():
            return seriesofbrand(None, None, brand_input, msg)
        else:
            return u"The Input brand have not been included in mom_baby system!"
    
def hello(request):
    return HttpResponse("Hello world")

def brands(request):
    return HttpResponse("\n".join(QueryHandler.Brands()))

@profile("1000.prof")
def seriesofbrand(request, ebrand, brand=None, msg={'ToUserName':'lilei', 'FromUserName':'hanmeimei'}):
    branda = brand if brand else QueryHandler.EBrand2Brand[ebrand] 
    show_list = QueryHandler.Series(branda)
    c = Context({
             'ToUserName' : msg['ToUserName'],
             'FromUserName': msg['FromUserName'],
             'createTime': str(int(time.time())),
             'series_list': __renderShowList(show_list),
             'series_count': len(show_list),
             'msgtype' : 'news'
             })
    fp = open(TEMPLATE_DIRS[0] + '/series_templ')
    t = Template(fp.read())
    fp.close()
    
    html = t.render(c)
    return HttpResponse(html)

def __renderShowList(show_list):
    contextlist = []
    for item in show_list:
        showdict = {}
        showdict['seriesName'] = item.name
        showdict['title'] = u'%s the lowest price: %d yuan %dg' % (item.tunnel, item.price, item.volume)
        showdict['picurl'] = item.pic_link
        showdict['url'] = u"http://%s/series/%s/trend" % ('10.31.186.63', QueryHandler.Series2ESeries[item.name])
        contextlist.append(showdict)
    return contextlist
       
@profile("2000.prof") 
def trendofseries(request, series):
    data = QueryHandler.TrendDataOfSeries(series, 10, 3)
    html =  RenderSeriesCharts(data, series)
    return HttpResponse(html)   

def trendofbrand(request, brand):
    data = QueryHandler.TrendDataOfBrand(u'\u60e0\u6c0f', 10, 3)
    html = RenderBrandCharts(data, brand)
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
    fp = open(TEMPLATE_DIRS[0] + '/chart_templ')
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
    fp = open(TEMPLATE_DIRS[0] + '/chart_templ')
    t = Template(fp.read())
    fp.close()
    #dict = { "S-26" : { 1:{ 'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 2:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 3:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}, 4:{'suning': [0.1,0.2,0.3,0.4], 'tmall' : [0.1,0.2,0.3,0.4]}} } 

    brandname = QueryHandler.BrandName(series)
    isbrand_passed = True if brandname else False
    origDict = {}
    origDict[series] = dictdata
    chartdata_list = preprocessTrendData(origDict)
    c = Context({
                 'brand_passed' : isbrand_passed,
                 'brand' : brandname,
                 'series_list': origDict.items(),
                 'chartdata_list': chartdata_list,
                 'realchartIds' : [ (item[0], item[0].replace('_','-')) for item in chartdata_list ]
                 })
    return t.render(c)



