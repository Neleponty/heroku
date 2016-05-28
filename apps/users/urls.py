from django.conf.urls import url
from apps.users.views import UserRegistration, UserLogin, UserLogout, UserAccountEdit, UserCabinLoader

urlpatterns = [
    url(r'login/$', UserLogin.as_view()),
    url(r'logout/$', UserLogout.as_view()),
    url(r'registry/$', UserRegistration.as_view()),
    url(r'toEdit/$', UserAccountEdit.as_view()),
    url(r'UserBank', UserCabinLoader.as_view())
]
