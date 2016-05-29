from django.conf.urls import url, include

from apps.vacancies import views

urlpatterns = [
    url(r'createVacancy', views.VacancyRegistrationView.as_view()),
    url(r'registryFeedback', views.FeedbackIncrementHandler.as_view()),
    url(r'lookAtFeedback', views.FeedersListLoader.as_view()),
    url(r'edit$', views.VacancyEditView.as_view()),
]
