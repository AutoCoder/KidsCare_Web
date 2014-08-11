from django.conf.urls import patterns, include, url

from django.contrib import admin
from views import hello, seriesofbrand, trendofseries, handleWXHttpRequest#, trendofbrand
from settings import STATICFILES_DIRS
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', handleWXHttpRequest),
    url(r'^hello/$', hello),
    url(r'^brand/(.*)/series/$', seriesofbrand),
    #url(r'^brand/(.*)/trend/$', trendofbrand),
    url(r'^series/(.*)/trend/$', trendofseries),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':str(STATICFILES_DIRS[0]), 'show_indexes': True}),
)