import hashlib
import time
import xml.etree.ElementTree as ET
from MilkQueryHandler import QueryHandler
from models import WxUserinput
from django.template import Template, Context
from kidscare.settings import TEMPLATE_DIR, MOMBABY_HOST

class WeiXinHandler:
    
    @staticmethod
    def checkSignature(request):
        """
        This method is for wx api, which will return a signature to make sure this site is for a specified weixin Subscribe-Service
        """
        token = "mombaby"  # TOKEN setted in weixin
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
            #record the wx user input for data Analysis later
            WeiXinHandler.record_wxuserinput(msg)
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
        brandlistStr = u"\u8bf7\u8f93\u5165\u54c1\u724c\u540d\u79f0\u6216\u5e8f\u53f7\uff1a\n";
        for idx in xrange(1, len(brands)+1):
            brandlistStr += u"(%d) %s     " % (100 + idx, brands[idx])
            if idx % 3 == 0:
                brandlistStr += u'\n'
        
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'content' : brandlistStr,
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIR + '/text_templ')
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
                showdict['picurl'] = QueryHandler.getPicLinkforSeries(item.name)#item.pic_link
                showdict['url'] = u"http://%s/milk/series/%s/trend" % (MOMBABY_HOST, QueryHandler.Series2ESeries[item.name])
                contextlist.append(showdict)
            return contextlist 
        
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'series_list': renderShowList(show_list),
                 'series_count': len(show_list),
                 'msgType' : 'news'
                 })
        fp = open(TEMPLATE_DIR + '/series_templ')
        t = Template(fp.read())
        fp.close()
    
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod
    def response_subscribe(msg):
        welcome_str = u"""\u672c\u53f7\u7684\u76ee\u6807\u662f\uff1a\u5feb\u901f\u67e5\u8be2\u5f53\u524d\u5404\u5927\u7535\u5546\u6700\u4f4e\u4ef7\uff0c\u64b8\u5c3d\u5404\u79cd\u7f8a\u6bdb\u3002\u000d\u000a\u56de\u590d\u5976\u7c89\u54c1\u724c\u5982\u3010\u60e0\u6c0f\u3011\uff0c\u67e5\u8be2\u5f53\u524d\u5404\u5927\u7535\u5546\u6700\u4f4e\u4ef7\u000d\u000a\u56de\u590d\u3010\u5976\u7c89\u3011\uff0c\u67e5\u8be2\u672c\u53f7\u6536\u5f55\u7684\u6240\u6709\u5976\u7c89\u54c1\u724c"""
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'content' : welcome_str,
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIR + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod 
    def response_wronginput(msg):
        reply_templ = u"\u60a8\u8f93\u5165\u7684\u5976\u7c89\u54c1\u724c\u672c\u53f7\u6682\u65f6\u4e0d\u652f\u6301"
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'content' : reply_templ,
                 'msgType' : 'text'
                 })
        fp = open(TEMPLATE_DIR + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
    
    @staticmethod
    def record_wxuserinput(msg):
        try:
            wxinput = WxUserinput(input=msg['Content'],wxuseraccout=msg['FromUserName'])
            wxinput.save()
        except Exception, info:
            print "exceptions %s" % info