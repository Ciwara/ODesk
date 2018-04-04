"""migrants URL Configuration

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

from django.conf.urls import url
from migrants import views

urlpatterns = [
    url(r'^table$', views.table, name='table'),
    url(r'^person/(?P<pk>.*)', views.person, name='person'),
    url(r'^person-table/(?P<iid>.*)', views.person_table, name='person_table'),
    url(r'^survey-table/$', views.survey_table, name='survey_table'),
    # url(r'^chart/$', chart, name='chart'),
    url(r'^$', views.dashboard, name='dashboard_mig')
]
