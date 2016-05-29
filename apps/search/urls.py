from django.conf.urls import url
from apps.search.views import ProjectSearchView

urlpatterns = [
    url('projects/$', ProjectSearchView.as_view())
]
