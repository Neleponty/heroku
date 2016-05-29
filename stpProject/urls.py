"""stpProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from apps.site_root.views import HeadPageLoader
from apps.vacancies.views import LoadVacancyPage
from stpProject import settings
from stpProject.apps import DocumentLoader
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^group/', include('apps.projects.urls')),
    url(r'^$', HeadPageLoader.as_view()),
    url(r'^users/', include('apps.users.urls')),
    url(r'^siteRoot/', include('apps.site_root.urls')),
    url(r'^vacancy/$', LoadVacancyPage.as_view()),
    url(r'^vacancy/', include('apps.vacancies.urls')),
    url(r'^search/', include('apps.search.urls')),
    url(r'^download/media(.+)$', DocumentLoader.as_view()),  # to get
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # to post_form

]
urlpatterns += staticfiles_urlpatterns()
