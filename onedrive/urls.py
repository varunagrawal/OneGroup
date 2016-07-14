from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^login/$', views.login, name="login"),
    url(r'^authenticate/$', views.authenticate, name="authenticate"),
    url(r'^approot/$', views.approot, name="approot"),
]
