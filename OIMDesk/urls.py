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
from django.conf.urls import url, include
from django.contrib import admin
# from desk.views import admin as admin_
from desk.views import dashboard

admin.site.site_header = 'DNDS-Desk admin'
admin.site.site_title = 'DNDS-Desk admin'
# admin.site.site_url = 'http://coffeehouse.com/'
admin.site.index_title = 'DNDS-Desk administration'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', dashboard.user_dashboard, name='index'),
    # url(r'^user-new/$', views.user_new, name='user_new'),
    # url(r'^user-manager/$', views.user_manager, name='user_manager'),
    # url(r'^user-change/(?P<pk>.*)$', views.user_change, name='user_change'),

    url(r'^migrants/', include('migrants.urls')),
    url(r'^rapatrie/', include('repatriate.urls')),

    url(r'^login/$',
        auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
