import sys
import os
import socket
import datetime
import smtplib  
from email.mime.text import MIMEText

if socket.gethostname() == 'iZ23otdlkscZ':
    sys.path.append('/root/kidscare_src/KidsCare_Web/kidscare')
else:
    sys.path.append('E:/OpenSource/Spider_praitise/KidsCare_mobilesite/KidsCare_Web/kidscare')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kidscare.settings")

from mombabyprods.models import MilkProd, MilkSeries
from kidscare.settings import TEMPLATE_DIR
from django.template import Template, Context

def CheckIsCheapestWithdiscount(series_name, duration):
	now = datetime.datetime.now()
	duration_begin = now - duration # 1 month : datetime.timedelta(hours=719, minutes=59, seconds=59) 
	cheapestProds = MilkProd.objects.filter(name=series_name, volume__lte=2000, scrapy_time__gt=duration_begin).order_by('-unitprice')
	if cheapestProds:
		cheapestProd = cheapestProds[0]
		today_begin = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
		if True: #cheapestProd.scrapy_time > today_begin:
			avg_utprice = sum([item.unitprice for item in cheapestProds])/len(cheapestProds)
			return cheapestProd, (cheapestProd.unitprice/avg_utprice)
		else:
			return None, 1
	else:
		return None, 1

def FindAllYangMao(duration=datetime.timedelta(hours=719, minutes=59, seconds=59), discount_threshold = 0.9):
	results = []
	for serie in MilkSeries.objects.all():
		item, discout = CheckIsCheapestWithdiscount(serie.name, duration)
		if item and True: #discout < discount_threshold:
			results.append(item)

	return results

def send_mail(to_list,sub,content):   
    mail_host="SMTP.163.com"  
    mail_user="kidscare1"    
    mail_pass="wodemima123"    
    mail_postfix="163.com"  
    me="Kidscare_Notifier"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='html',_charset='utf-8')  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP('smtp.163.com')  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False  

if __name__ == "__main__":

    results = FindAllYangMao()
    if results:
        fp = open(TEMPLATE_DIR + '/email_templ')
        t = Template(fp.read())
        fp.close()
        c = Context({
                     'results' : results,
                     })
        html = t.render(c)
        send_mail(["tj_liyuan@163.com",],"kidscare_notification", html)
