import sys
import os
import socket

if socket.gethostname() == 'iZ23otdlkscZ':
    sys.path.append('/root/kidscare_src/KidsCare_Web/kidscare')
else:
    sys.path.append('E:/OpenSource/Spider_praitise/KidsCare_mobilesite/KidsCare_Web/kidscare')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kidscare.settings")

from mombabyprods.models import MilkBrand, WxUserinput

if __name__ == "__main__":

    brands = MilkBrand.objects.all()
    for brand in brands:
        brand.querycount = WxUserinput.objects.filter(input=brand.name).count()
        brand.save()
    
    brands = MilkBrand.objects.all().order_by('-querycount')
    
    rank = 1
    for brand in brands:
        brand.queryrank = rank
        rank += 1
        brand.save()
