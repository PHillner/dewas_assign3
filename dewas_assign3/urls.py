"""dewas_assign3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
# from django.contrib import admin
from blog.views import home
from blog.views import blog
from blog.views import edit
from blog.views import add
from blog.views import delete

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^/blog/', home),
    url(r'^/blog/(?P<id>\d+)/$', blog),
    url(r'^/edit/(?P<id>\d+)/$', edit),
    url(r'^/add/', add),
    url(r'^/delete/(?P<id>\d+)/$', delete),
]
