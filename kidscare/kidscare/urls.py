from django.conf.urls import patterns, include, url

from django.contrib import admin
from views import hello, brands, seriesofbrand, trendofbrand, trendofseries
from settings import STATICFILES_DIRS
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', hello),
    url(r'^brands/$', brands),
    url(r'^brand/(.*)/series/$', seriesofbrand),
    url(r'^brand/(.*)/trend/$', trendofbrand),
    url(r'^series/(.*)/trend/$', trendofseries),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':str(STATICFILES_DIRS[0]), 'show_indexes': True}),
)