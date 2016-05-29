from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from apps.users.models import Student

'''
    this module create custom backend to Student
    it help to use Student without Foreign key on django_User model
    it easier then first one
    this backend has link on itself in Settings of project
'''


class CustomUserModelBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_class.objects.get(username=username)
            if user.password == password:
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = Student
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model-_-CustomRise')
        return self._user_class
