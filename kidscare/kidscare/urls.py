from django.conf.urls import patterns, include, url

from django.contrib import admin
from settings import STATICFILES_DIRS
from views import hello
from mombabyprods.views import handleWXHttpRequest

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^milk/', include('kidscare.mombabyprods.urls')),
    url(r'^$', handleWXHttpRequest), # for weixin handler
    url(r'^hello/$', hello),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':str(STATICFILES_DIRS[0]), 'show_indexes': True}),
)