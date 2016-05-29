from django.conf.urls import url

from apps.projects import views

urlpatterns = [
    url(r'edit/base', views.LoadFoundationEditForm.as_view()),
    url(r'edit/doc', views.FormToDocsEditing.as_view()),
    url(r'edit/members', views.FormToMembersEditing.as_view()),
    url(r'edit/events', views.LoadEventForm.as_view()),
    url(r'topList', views.LoadTopList.as_view()),
    url(r'GroupBank', views.LoadPage.as_view()),
    url(r'registry/$', views.FormToProjectRegistration.as_view()),
]
