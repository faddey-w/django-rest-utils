from django.conf.urls import patterns, include, url
from django.contrib import admin

from dummy.application.urls import urlpatterns as app_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'app/(?P<arg_one>[^/.]+)/(?P<arg_two>[^/.]+)/', include(app_urlpatterns)),
    # url(r'app/(?P<arg_one>[^/.]+)/', include(app_urlpatterns)),
    # url(r'app/', include(app_urlpatterns)),
)
