from django.conf.urls import patterns, url

from views import seriesofbrand, trendofseries

urlpatterns = patterns('',
    url(r'^brand/(.*)/series/$', seriesofbrand),
    url(r'^series/(.*)/trend/$', trendofseries),
)
    #url(r'^brand/(.*)/trend/$', trendofbrand),