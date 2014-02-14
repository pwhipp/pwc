from django.conf.urls import patterns, url
from hitcount.views import update_hit_count_ajax

urlpatterns = patterns('',
    url(r'^hitcount_update/$',
        update_hit_count_ajax,
        name='hitcount_update_ajax'))