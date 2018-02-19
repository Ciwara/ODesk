"""OIMDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib import admin

from desk.views import (
    dashboard, index, table, person_table, survey_table, person)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name='index'),
    url(r'^table$', table, name='table'),
    url(r'^person/(?P<pk>.*)', person, name='person'),
    url(r'^person-table/(?P<iid>.*)', person_table, name='person_table'),
    url(r'^survey-table/$', survey_table, name='survey_table'),
    # url(r'^chart/$', chart, name='chart'),
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^login/$',
        auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

