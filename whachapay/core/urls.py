from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    (r'^$', 'home'),
    (r'^update_selections/$', 'ajax_home_update_selections'),
    (r'^dealer_select/$', 'dealer_select'),
    (r'^entry/(?P<place_id>[a-f0-9]{40})/$', 'deal_entry'),
    (r'^deal_entered/$', 'deal_entered'),
    (r'^area_summary/$', 'area_summary'),
    (r'^dealer_deals/(?P<place_id>[a-f0-9]{40})/$', 'dealer_deals'),
    (r'^deal/(?P<deal_pk>\d+)/$', 'deal_detail'),
)
