"""repatriate URL Configuration

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
from repatriate import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard_rep'),
    url(r'^desk-controle$', views.desk_controle, name='controle'),
    url(r'^desk-monitoring$', views.desk_monitoring, name='monitoring'),
    url(r'^target_validated/(?P<pk>.*)', views.target_validated, name='tvalidated'),
    url(r'^target-correction/(?P<id>.*)', views.target_correction, name='correction_target'),
    url(r'^person-correction/(?P<id>.*)', views.person_correction, name='correction_person'),
    url(r'^export-xls/(?P<start>.*)/(?P<end>.*)', views.export_xls, name='export_xls'),
]
