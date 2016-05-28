# coding=utf8
import datetime
import re
from django.contrib.auth.models import Group, GroupManager
from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.forms import Textarea
from apps.users.models import Student
from stpProject.apps import date_across_days

GROUP_CATEGORY = (
    ('Sports', 'Спорт'),
    ('Art', 'Искусство'),
    ('Intel', 'Интеллектуальная деятельность')
)

TEAM_STATUS = {
    'Start': "Проект не зарегистрирован",
    'Find': "Поиск союзников",
    'Active': "Проект активен",
    'Released': "Проект в релизе"
}

MEMBER_STATUS = ["Работает над проектом", "Отстранен", 'CREATOR']


class Project(Group):
    members = models.ManyToManyField(
        Student,
        through='Membership',
        through_fields=('project', 'member'),
        blank=True
    )
    title = models.CharField('Название', max_length=30, default="Unnamed")
    category = models.CharField('Категория', choices=GROUP_CATEGORY, max_length=30, default='Sport')
    status = models.CharField(max_length=30, blank=True)
    pub_date = models.DateField(auto_now=True, editable=False)
    release_date = models.DateField(auto_now=False, default=date_across_days(3))
    describe = models.CharField('Описание', max_length=6000, default="Описание проекта одним абзацем")
    logo = models.ImageField('Лого', max_length=300, null=True, blank=True, default='default.jpg')  # as link on file
    rate = models.CharField(max_length=300, blank=True)  # as link on file
    admin = Student()

    objects = GroupManager()

    def get_admin(self):
        return Membership.admin_as_membership(self).member

    def is_member(self, user):
        return user in self.members.all()

    def is_admin(self, user):
        if user.is_anonymous():
            return False
        return Student.get_by_name(user.username) == Membership.admin_as_membership(self).member

    def __str__(self):
        return self.id

    def time_before_release(self):
        return self.release_date - datetime.date.today()

    def finish_project(self):
        is_formed = self.status is not TEAM_STATUS['Start'] and self.pub_date <= datetime.date.today()
        if is_formed:
            self.status = TEAM_STATUS['Released']
        else:
            self.delete()

    @staticmethod
    def get_by_bounds(bottom, top):
        return Project.objects.all()[bottom:top]

    @staticmethod
    def get_by_name(group_name):
        return Project.objects.get(name=group_name)

    @staticmethod
    def set_admin_or_create_it(user, project):
        any_members_exists = Membership.objects.filter(member=user, project=project).count() > 0
        if any_members_exists:
            relation = Membership.objects.get(member=user, project=project)
            relation.status = MEMBER_STATUS[2]
            relation.save()
        else:
            m = Membership.objects.create(
               project=project,
               member=user,
               status=MEMBER_STATUS[2],
               role='Создатель группы')
            m.save()


# intermediate class for many-to-many model relationship between students and their teams
class Membership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=60, default="anchor")
    registration_date = models.DateField(auto_now=True)

    # exclude the possibility of adding the same user
    @staticmethod
    def not_contains(project, member):
        return Membership.objects.filter(project=project, member=member).count() <= 1

    @staticmethod
    def status_worker():
        return MEMBER_STATUS[0]

    @staticmethod
    def status_expelled():
        return MEMBER_STATUS[1]

    @staticmethod
    def status_admin():
        return MEMBER_STATUS[2]

    @staticmethod
    def upgrade_to_member(form, project):
        member = form.cleaned_data['member']
        if Membership.not_contains(project, member):
            mm_ship = form.save(commit=False)
            mm_ship.project = project
            mm_ship.status = Membership.status_worker()
            mm_ship.save()

    @staticmethod
    def delete_from_project(form, project):
        m = Membership.objects.get(project=Project.get_by_name(project),
                                   member=form.cleaned_data['member'])
        m.status = Membership.status_expelled()
        m.save()

    @staticmethod
    def all_without_admin(project):
        return Membership.objects.filter(project=project).exclude(status=Membership.status_admin())

    @staticmethod
    def all_active_workers(project):
        return Membership.all_without_admin(project).exclude(status=Membership.status_expelled())

    @staticmethod
    def admin_as_membership(project):
        return Membership.objects.get(project=project, status=Membership.status_admin())

    @staticmethod
    def get_all_relations_by_member(member):
        return Membership.objects.filter(member=member)

    @staticmethod
    def try_create_relations(current_project, user):
        # is need to save project before to create membership relation
        current_project.save()
        # create admin and save it with all_users
        Membership.objects.create(project=current_project, member=user)
        Project.set_admin_or_create_it(user, current_project)
        current_project.save()


class Event(models.Model):
    text = models.TextField(max_length=500)
    date = models.DateField(auto_now=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    objects = models.Manager()
    widgets = {
        'description': Textarea(attrs={'cols': 30, 'rows': 2}),
    }

    def __str__(self):
        return '%s: %s' % (self.date, self.text)


class Doc(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=True
    )
    describe = models.CharField(max_length=3000, blank=True)
    doc_src = models.FileField(max_length=300)
    # this field will be init after signal
    name = ""
    objects = models.Manager()

    # this signal will called after doc __init__
    # it save name for doc by doc path
    @staticmethod
    def get_file_name(file_url):
        p = re.compile('[0-9A-z_]+\.[0-9A-z_]+')
        result = p.findall(file_url)[0]
        if result is None:
            return "wrong file name"
        else:
            return result


@receiver(post_init, sender=Doc)
def init_name(sender, **kwargs):
    instance = kwargs['instance']
    if instance.doc_src:
        instance.name = sender.get_file_name(instance.doc_src.url)

