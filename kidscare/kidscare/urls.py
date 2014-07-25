from django.conf.urls import patterns, include, url

from django.contrib import admin
from views import hello, price_chart, brands, Series, trenddata
from settings import STATICFILES_DIRS
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', hello),
    url(r'^price/$', price_chart),
    url(r'^brands/$', brands),
    url(r'^Series/$', Series),
    url(r'^trenddata/$', trenddata),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':str(STATICFILES_DIRS[0]), 'show_indexes': True}),
)