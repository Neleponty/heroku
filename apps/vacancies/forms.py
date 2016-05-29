# coding=utf8
from django.forms import Textarea, ModelForm
from django.shortcuts import get_object_or_404

from apps.vacancies.models import Vacancy
from stpProject import static


class VacancyRegistrationForm(ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'worker_position', 'short_describe', 'any_contact', 'text']
        widgets = {
            'text': Textarea(attrs={'cols': 30, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(VacancyRegistrationForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, "Отправить")

    def try_edit(self):
        if self.is_valid():
            self.save()
            return True
        return False

    def try_save_vacancy(self, user, project):
        if project.is_admin(user) and self.is_valid():
            fill_form = self.save(commit=False)
            fill_form.project = project
            fill_form.save()
            return True
        return False