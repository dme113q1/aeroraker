from django.conf.urls import patterns, url
from aeroraker.views import MainView, TaskView, PriceView, TaskDetailView

urlpatterns = patterns(
    '',
    url(r'^$', MainView.as_view(), name="main"),
    url(r'^task/$', TaskView.as_view(), name='task'),
    url(r'^price/$', PriceView.as_view(), name='price'),
    url(r'^taskdetail/(?P<pk>\d+)/$', TaskDetailView.as_view(), name='taskdetail'),
)
