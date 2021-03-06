'''
Created on 2014.11.25

@author: tj_liyuan

'''
import urllib 
import urllib2 
#import cookielib 
import hashlib
import json 

class wxpublic:
    def __init__(self, username, password, fakeid):
        self.token = ''
        self.username = username
        self.password = password
        self.fakeid = fakeid
    
    def login(self):
        try:
            paras={ 'username': self.username,
                   'pwd': hashlib.md5(self.password).hexdigest().lower(), # md5 password
                   'imgcode':'',
                   'f':'json'
            }
            req = urllib2.Request('https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN',urllib.urlencode(paras))
            req.add_header('Accept','application/json, text/javascript, */*; q=0.01') 
            req.add_header('Accept-Encoding','gzip,deflate,sdch') 
            req.add_header('Accept-Language','zh-CN,zh;q=0.8') 
            req.add_header('Connection','keep-alive') 
            #req.add_header('Content-Length','79') 
            req.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8') 
            req.add_header('Host','mp.weixin.qq.com') 
            req.add_header('Origin','https://mp.weixin.qq.com') 
            req.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN') 
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36') 
            req.add_header('X-Requested-With','XMLHttpRequest') 
            ret = urllib2.urlopen(req) 
            retread = ret.read() 
            #print retread 
            token = json.loads(retread)
            self.token = token['redirect_url'][44:] 
            return self.token
        except Exception, info:
            self.token = ''
            print info
    
    def groupsend(self, content):
        try:
            if not self.token:
                print "please login first..."
                return 
            paras2={
                    'type':'1',
                    'content': content,
                    'error':'false',
                    'imgcode':'',
                    'tofakeid': self.fakeid,
                    'token': self.token,
                    'ajax':'1'
            }
            req2 = urllib2.Request('https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&amp;lang=zh_CN',urllib.urlencode(paras2)) 
            req2.add_header('Accept','*/*') 
            req2.add_header('Accept-Encoding','gzip,deflate,sdch') 
            req2.add_header('Accept-Language','zh-CN,zh;q=0.8') 
            req2.add_header('Connection','keep-alive') 
            #req2.add_header('Content-Length','77')  -> this line will raise BadStatusLine
            req2.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8') 
            req2.add_header('Host','mp.weixin.qq.com') 
            req2.add_header('Origin','https://mp.weixin.qq.com') 
            req2.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/singlemsgpage?msgid=&source=&count=20&amp;t=wxm-singlechat&amp;fromfakeid=150890&token=%s&lang=zh_CN' % self.token) 
            req2.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36') 
            req2.add_header('X-Requested-With','XMLHttpRequest') 
    
            #req2.add_header('Cookie',cookie2) 
            ret2=urllib2.urlopen(req2) 
            #ret2=opener.open(req2) 
            print 'x',ret2.read() 
        except Exception, info:
            print "send content to all failed.."
            print info
            
                
    def logout(self):
        pass
    
if __name__ =='__main__':  
    wx_sub = wxpublic("2693050072@qq.com","wodemima123","2398793139")
    #wx_sub = wxpublic("694830047","diudiu88")
    if wx_sub.login():
        content = "just for testing..."
        wx_sub.groupsend(content)