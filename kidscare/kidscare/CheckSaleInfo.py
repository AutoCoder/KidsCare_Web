import sys
import os
import socket

if socket.gethostname() == 'iZ23otdlkscZ':
    sys.path.append('/root/kidscare_src/KidsCare_Web/kidscare')
else:
    sys.path.append('E:/OpenSource/Spider_praitise/KidsCare_mobilesite/KidsCare_Web/kidscare')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kidscare.settings")

from mombabyprods.models import MilkProd, MilkSeries

def CheckIsCheapest(series_name, duration):
	now = datetime.datetime.now()
	duration_begin = now - duration # 1 month : datetime.timedelta(hours=719, minutes=59, seconds=59) 
	cheapestProd = MilkProd.objects.filter(name=series_name, volume__lte=2000, scrapy_time__gt=duration_begin).order_by('-unitprice')[0]
	today_begin = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
	if cheapestProd.scrapy_time > today_begin:
		return cheapestProd
	else:
		return None

def FindAllYangMao(duration=datetime.timedelta(hours=719, minutes=59, seconds=59)):
	results = []
	for serie in MilkSeries.objects.all():
		item = CheckIsCheapest(serie.name, duration)
		if item:
			result.append(item)

	return results