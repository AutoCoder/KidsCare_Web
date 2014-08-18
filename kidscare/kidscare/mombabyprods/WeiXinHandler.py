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
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'content' : "\n".join(brands),
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
                showdict['picurl'] = item.pic_link
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
        welcome_str = u"""\u6b22\u8fce\u5173\u6ce8\u6bcd\u5a74\u7528\u54c1\u6bd4\u4ef7\u5fae\u4fe1\u53f7\uff0c\u53ef\u4ee5\u56de\u590d\u5976\u7c89\u54c1\u724c\u5982\u60e0\u6c0f\uff0c\u67e5\u8be2\u5f53\u524d\u5404\u5927\u7535\u5546\u6700\u4f4e\u4ef7\uff08\u56de\u590d\u5976\u7c89\u67e5\u8be2\u5f53\u524d\u6536\u5f55\u7684\u54c1\u724c\uff09"""
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