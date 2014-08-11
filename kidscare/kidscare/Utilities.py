from mombabyprods.models import MilkBrand, MilkSeries, MilkProd, MilkTunnel
import sys

class utilities(object):
    
    @staticmethod
    def UpdateBrandSeries():
        """
        delete the existed table of MilkBrand, and then insert the table with the new selected ones from MilkProds
        delete the existed table of MilkSeries, and then insert the table with the new selected ones from MilkProds
        """
        MilkSeries.objects.all().delete()
        MilkBrand.objects.all().delete()
        MilkTunnel.objects.all().delete()
        brandlist = [item.brand for item in MilkProd.objects.all()]
        unique_brandlist = {}.fromkeys(brandlist).keys()
        for item in unique_brandlist:
            b = MilkBrand(name=item)
            b.save()
        
        for brandstr in unique_brandlist:
            brandset = MilkProd.objects.filter(brand=brandstr)
            serieslist = [item.name for item in brandset]
            unique_series = {}.fromkeys(serieslist).keys()
            for ser in unique_series:
                s = MilkSeries(name=ser, BrandIn=brandstr)
                s.save()
        
        tunnellist = [item.tunnel for item in MilkProd.objects.all()]
        unique_tunnellist = {}.fromkeys(tunnellist).keys()
        for item in unique_tunnellist:
            t = MilkTunnel(name=item)
            t.save()        

# Create your tests here.
if __name__ == "__main__":
    if sys.argv is "updatedb":
        utilities.UpdateBrandSeries()
    else:
        pass