# coding=utf8
from django.db.models import Model
from django.db import models
from django.forms import ModelForm, Textarea
from apps.users.models import Student
from stpProject import static
from apps.projects.models import Project, Doc


class Vacancy(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True)
    title = models.CharField('Заголовок вакансии', max_length=40, default='')
    text = models.CharField('Основной текст', max_length=5000, default='')
    short_describe = models.CharField('Краткое описание', max_length=400, default='')
    worker_position = models.CharField('Кого ищем', max_length=100, default='')  # for fast search
    any_contact = models.CharField('Контактная информация', max_length=100, default='')  # phone number or url
    # text_doc = models.ForeignKey(Doc, max_length=300, default='default.txt', blank=True)  # todo:complete it
    pub_date = models.DateField(auto_now_add=True, blank=True)

    def feedback_count(self):
        count = RelationToFeedback.get_members_by_vacancy(self)
        if count is not None:
            return len(count)
        else:
            return 0

    @staticmethod
    def get_by_bounds(bottom, top):
        return Vacancy.objects.all()[bottom:top]

    # todo: x2
    # # restrict base file formats as .docs only
    # def clean(self):
    #     cleaned_data = super(Vacancy, self).clean()
    #     file = cleaned_data.get('text_doc')
    #     return cleaned_data

    @staticmethod
    def get_vacancies_by_project(project):
        return Vacancy.objects.filter(project=project)

    @staticmethod
    def get_by_id(id):
        return Vacancy.objects.get(pk=id)

    def is_unique_feedback_with(self, user):
        result_array = RelationToFeedback.objects.filter(vacancy=self, member=user).count()
        return result_array == 0


class RelationToFeedback(Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    member = models.ForeignKey(Student, on_delete=models.CASCADE)

    @staticmethod
    def get_members_by_vacancy(vacancy):
        temp = RelationToFeedback.objects.filter(vacancy=vacancy)
        relate = []
        for relation in temp:
            relate.append(relation.member)
        return relate

    @staticmethod
    def get_vacancies_by_member(member):
        temp = RelationToFeedback.objects.filter(member=member)
        relate = []
        for relation in temp:
            relate.append(relation.vacancy)
        return relate

