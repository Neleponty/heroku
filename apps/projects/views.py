# coding=utf8
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.utils import render_crispy_form
from django.forms.models import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template.context_processors import csrf
from django.views.generic import View
from apps.projects import models
from apps.projects import forms
from apps.projects.models import TEAM_STATUS, Membership, Project
from apps.vacancies.models import Vacancy
from stpProject.static import get_static_context, UrlKeeper


# extend all our view
class CustomView(View):
    @staticmethod
    def init_context(request, group_name, title):
        c = {'success_message': 'successful edited',
             'registration_title': title,
             'replace_to_url': '/group/GroupBank?groupName=' + group_name}
        c.update(csrf(request))
        return c

    @staticmethod
    def json_answer_if_success():
        return {'success': True}

    @staticmethod
    def json_answer_if_fail(request, form):
        c = {}
        c.update(csrf(request))
        form_html = render_crispy_form(form, context=c)
        return {'success': False, 'form_html': form_html}


class LoadPage(CustomView):
    def get(self, request, *args, **kwargs):
        user = request.user
        project = models.Project.get_by_name(request.GET['groupName'])
        if project.is_admin(user):
            return render_to_response('projects/group_admin_vision.html', self.main_page_content(user, project))
        else:
            return render_to_response('projects/groups.html', self.main_page_content(user, project))

    @staticmethod
    def main_page_content(user, project):
        all_vacancies = Vacancy.get_vacancies_by_project(project)
        c = get_static_context(user)
        c.update({
            "group": project,
            "memberships_without_admin": models.Membership.all_without_admin(project),
            "groupAdminMembership": models.Membership.admin_as_membership(project),
            "DayEvent": models.Event.objects.filter(project=project).order_by('date').first(),
            "docs": models.Doc.objects.filter(project=project),
            "vacancies": all_vacancies,
        })
        return c


class FormToProjectRegistration(CustomView):
    def get(self, request, *args, **kwargs):
        c = {"form": forms.ProjectForm(), "registration_title": "Регистрация проекта",
             "success_message": "Регистрация успешно завершена", 'replace_to_url': '/'}
        c.update(csrf(request))
        return render_to_response('../templates/registration/registration_form.html', c)

    def post(self, request, *args, **kwargs):
        fill_form = forms.ProjectForm(request.POST or None, request.FILES)
        if self.try_save_group(fill_form, request.user):
            return JsonResponse(self.json_answer_if_success())
        else:
            return JsonResponse(self.json_answer_if_fail(request, fill_form))

    @staticmethod
    def try_save_group(form, user):
        if form.is_valid():
            # create table at first
            current_project = form.save(commit=False)
            current_project.status = TEAM_STATUS['Start']
            current_project.rate = 0
            Membership.try_create_relations(current_project, user)
            return True
        return False


# top list of projects on main page
class LoadTopList(View):
    def get(self, request, *args, **kwargs):
        short_groups = models.Project.get_by_bounds(request.GET['bottom'], request.GET['top'])
        c = {"shortGroups": short_groups,
             "GroupBank": UrlKeeper.KeyUrlPairs['GroupBank'],
             "bottom": request['bottom'] + 10,
             "top": request['top'] + 10}

        return render_to_response('projects/groups_short_describe.html', c)


# edit base information about group
class LoadFoundationEditForm(CustomView):
    def get(self, request, *args, **kwargs):
        name = request.GET['groupName']
        fill_edit_form = forms.ProjectEditFoundationForm(instance=models.Project.get_by_name(name))
        # set base settings
        c = self.init_context(request, name, 'Edit base params')
        c.update({'form': fill_edit_form, '': ''})  # hint
        return render_to_response('registration/registration_form.html', c)

    def post(self, request, *args, **kwargs):
        project = models.Project.get_by_name(request.GET['groupName'])
        form = forms.ProjectEditFoundationForm(request.POST, request.FILES)
        if form.is_valid():
            if project.is_admin(request.user):
                project = self.build_project(form, project)
                project.save()
                return JsonResponse(self.json_answer_if_success())
        else:
            return JsonResponse(self.json_answer_if_fail(request, form))

    @staticmethod
    def build_project(form, current_project):
        project = current_project
        project.title = form.cleaned_data['title']
        project.describe = form.cleaned_data['describe']
        project.logo = form.cleaned_data['logo']
        return project


class FormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.render_required_fields = True
        self.add_input(Submit('submit', 'Сохранить'))


class FormToMembersEditing(CustomView):
    doc_formset_container = modelformset_factory(Membership, fields=['member', 'role'], can_delete=True, extra=1,
                                                 max_num=5, validate_max=True)

    def get(self, request, *args, **kwargs):
        group_name = request.GET['groupName']
        project = Project.get_by_name(request.GET['groupName'])
        starting_values = Membership.all_active_workers(project)
        c = self.init_context(request, group_name, 'Edit members')
        c.update({'formset': self.doc_formset_container(queryset=starting_values),
                  'helper': FormSetHelper()})
        return render(request, 'registration/registration_formset.html', c)

    def post(self, request, *args, **kwargs):
        all_forms = self.doc_formset_container(request.POST, request.FILES)
        name = request.GET['groupName']
        project = models.Project.get_by_name(name)
        if project.is_admin(request.user) and all_forms.is_valid():
            self.save_not_marked(self, all_forms, project)
            self.delete_marked(all_forms, project)
            return HttpResponseRedirect(UrlKeeper.render_group_bank_url(name))

        c = self.init_context(request, name, 'Edit you docs')
        c.update({'formset': all_forms, 'helper': FormSetHelper()})
        return render(request, 'registration/registration_formset.html', c)

    @staticmethod
    def save_not_marked(self, all_forms, project):
        for form in all_forms:
            if form.is_valid() & self.is_not_for_delete(form, all_forms):
                models.Membership.upgrade_to_member(form, project)

    @staticmethod
    def is_not_for_delete(form, all_forms):
        if form not in all_forms.deleted_forms:
            return True
        else:
            return False

    @staticmethod
    def delete_marked(all_forms, project):
        for deleted_form in all_forms.deleted_forms:
            models.Membership.delete_from_project(deleted_form, project)


class FormToDocsEditing(CustomView):
    doc_formset_container = modelformset_factory(models.Doc, fields=['doc_src', 'describe'], can_delete=True, extra=1,
                                                 max_num=5, validate_max=True)

    def get(self, request, *args, **kwargs):
        name = request.GET['groupName']
        fill_set = self.doc_formset_container(
            queryset=models.Doc.objects.filter(project=models.Project.get_by_name(name)), )
        c = self.init_context(request, name, 'Edit you documents')
        c.update({'formset': fill_set,
                  'helper': FormSetHelper()})
        return render(request, 'registration/registration_formset.html', c)

    def post(self, request, *args, **kwargs):
        all_forms = self.doc_formset_container(request.POST, request.FILES)
        name = request.GET['groupName']
        current_project = models.Project.get_by_name(name)
        if current_project.is_admin(request.user):
            self.try_delete_marked(all_forms, current_project)
            self.try_save_not_marked(self, current_project, all_forms)
            return HttpResponseRedirect(UrlKeeper.render_group_bank_url(name))

        c = self.init_context(request, name, 'Edit you docs')
        c.update({'formset': all_forms, 'helper': FormSetHelper()})
        return render(request, 'registration/registration_formset.html', c)

    @staticmethod
    def try_save_not_marked(self, project, all_forms):
        for form in all_forms:
            if form.is_valid() & self.is_not_for_delete(form, all_forms):
                self.save_form(form, project)

    @staticmethod
    def is_not_for_delete(form, all_forms):
        if form not in all_forms.deleted_forms:
            return True
        else:
            return False

    @staticmethod
    def try_delete_marked(all_forms, current_project):
        for deleted_form in all_forms.deleted_forms:
            if deleted_form.is_valid():
                docs_to_delete = models.Doc.objects.get(project=current_project,
                                                        doc_src=deleted_form.cleaned_data['doc_src'])
                docs_to_delete.delete()

    @staticmethod
    def save_form(form, current_project):
        instance = form.save(commit=False)
        # because is_valid cant exclude empty at all
        if instance.doc_src is not '' and instance.describe is not '':
            instance.project = current_project
            instance.save()


class LoadEventForm(CustomView):
    group_name = ''

    def get(self, request, *args, **kwargs):
        global group_name
        group_name = request.GET['groupName']
        c = self.init_context(request, group_name, 'Event editing')
        c.update({'form': forms.ProjectEditEvent()})
        return render_to_response('registration/registration_form.html', c)

    def post(self, request, *args, **kwargs):
        fill_form = forms.ProjectEditEvent(request.POST)
        return JsonResponse(self.try_save(self, fill_form, request, request.user), )

    @staticmethod
    def try_save(self, form, request, user):
        global group_name
        project = models.Project.get_by_name(group_name)
        if form.is_valid() and project.is_admin(user):
            form_instance = form.save(commit=False)
            form_instance.project = models.Project.get_by_name(group_name)
            form_instance.save()
            return {'success': True}
        c = {}
        c.update(csrf(request))
        form_html = render_crispy_form(form, context=c)
        return {'success': False, 'form_html': form_html}
