from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^test/(?P<test_id>.{4})/$', 'riddler.views.test_index', name='test_index'),
    url(r'^test/(?P<test_id>.{4})/answering$', 'riddler.views.answering_question', name='answering_question'),
    url(r'^test/(?P<test_id>.{4})/(?P<series_id>\d+)/$', 'riddler.views.start_to_answer_series', name='start_to_answer_series'),
    url(r'^imperavi/', include('imperavi.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
