from django.http import HttpResponse
from django.template import Template, Context
from settings import TEMPLATE_DIRS, MOMBABY_HOST
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
        return HttpResponse(WeiXinHandler.checkSignature(request))
    elif request.method == 'POST':
        return HttpResponse(WeiXinHandler.response_msg(request))
    
def hello(request):
    return HttpResponse("Hello world")

@profile("1000.prof")
def seriesofbrand(request, ebrand, brand=None, msg={'ToUserName':'lilei', 'FromUserName':'hanmeimei'}):
    branda = brand if brand else QueryHandler.EBrand2Brand[ebrand] 
    return HttpResponse(WeiXinHandler.reponse_seriescharts(branda, msg))
       
@profile("2000.prof") 
def trendofseries(request, series):
    data = QueryHandler.TrendDataOfSeries(series, 10, 3)
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

class WeiXinHandler:
    
    @staticmethod
    def checkSignature(request):
        """
        This method is for wx api, which will return a signature to make sure this site is for a specified weixin Subscribe-Service
        """
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
        
    @staticmethod
    def response_msg(request):
        """
        This method is for wx api, which is the auto-response entry api, for now this method only support 'Brand', 'naifen' input.
        """
        recvmsg = request.body # 
        root = ET.fromstring(recvmsg)
        msg = {}
        for child in root:
            msg[child.tag] = child.text
            
        if msg["MsgType"] == "event":
            return WeiXinHandler.response_subscribe(msg)
        else:
            wxinput = msg["Content"]
            if wxinput in QueryHandler.Brand2EBrand.keys():
                return WeiXinHandler.reponse_seriescharts(wxinput, msg)
            elif wxinput == u'\u5976\u7c89': # unicode 'naifen'
                return WeiXinHandler.supported_brandlist(msg)
            else:
                return WeiXinHandler.response_wronginput(msg)
            
    @staticmethod
    def supported_brandlist(msg):
        brands = QueryHandler.Brands()
        c = Context({
                 'ToUserName' : msg['ToUserName'],
                 'FromUserName': msg['FromUserName'],
                 'createTime': str(int(time.time())),
                 'content' : "\n".join(brands),
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIRS[0] + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod
    def reponse_seriescharts(wxinput, msg):
        show_list = QueryHandler.Series(wxinput)
        
        def renderShowList(show_list):
            contextlist = []
            for item in show_list:
                showdict = {}
                showdict['seriesName'] = item.name
                showdict['title'] = u'%s %d\u6bb5%dg \u6700\u4f4e\u4ef7%d\u5143 ' % (QueryHandler.Tunnels2Ltunnels[item.tunnel], item.segment, item.volume, item.price )
                showdict['picurl'] = item.pic_link
                showdict['url'] = u"http://%s/series/%s/trend" % (MOMBABY_HOST, QueryHandler.Series2ESeries[item.name])
                contextlist.append(showdict)
            return contextlist 
        
        c = Context({
                 'ToUserName' : msg['ToUserName'],
                 'FromUserName': msg['FromUserName'],
                 'createTime': str(int(time.time())),
                 'series_list': renderShowList(show_list),
                 'series_count': len(show_list),
                 'msgType' : 'news'
                 })
        fp = open(TEMPLATE_DIRS[0] + '/series_templ')
        t = Template(fp.read())
        fp.close()
    
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod
    def response_subscribe(msg):
        welcome_str = u"""\u6b22\u8fce\u5173\u6ce8\u6bcd\u5a74\u7528\u54c1\u6bd4\u4ef7\u5fae\u4fe1\u53f7\uff0c\u53ef\u4ee5\u56de\u590d\u5976\u7c89\u54c1\u724c\u5982\u60e0\u6c0f\uff0c\u67e5\u8be2\u5f53\u524d\u5404\u5927\u7535\u5546\u6700\u4f4e\u4ef7\uff08\u56de\u590d\u5976\u7c89\u67e5\u8be2\u5f53\u524d\u6536\u5f55\u7684\u54c1\u724c\uff09"""
        c = Context({
                 'ToUserName' : msg['ToUserName'],
                 'FromUserName': msg['FromUserName'],
                 'createTime': str(int(time.time())),
                 'content' : welcome_str,
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIRS[0] + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod 
    def response_wronginput(msg):
        reply_templ = u"\u60a8\u8f93\u5165\u7684\u5976\u7c89\u54c1\u724c\u672c\u53f7\u6682\u65f6\u4e0d\u652f\u6301"
        c = Context({
                 'ToUserName' : msg['ToUserName'],
                 'FromUserName': msg['FromUserName'],
                 'createTime': str(int(time.time())),
                 'content' : reply_templ,
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIRS[0] + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
