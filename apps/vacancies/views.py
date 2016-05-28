# coding=utf8
from apps.projects.models import Project
from apps.projects.views import CustomView
from apps.site_root.views import build_top_list_content
from apps.vacancies.forms import VacancyRegistrationForm
from apps.vacancies.models import RelationToFeedback, Vacancy
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.template.loader import get_template
from django.views.generic import View
from stpProject.settings import EMAIL_HOST
from stpProject.static import UrlKeeper, get_static_context


# It load a vacancies list on main page
class LoadVacancyPage(View):
    def get(self, request, *args, **kwargs):
        content = get_static_context(request.user)
        content = build_top_list_content(0, 10, content)
        html_vacancies = self.build_vacancies_html_list(Vacancy.get_by_bounds(0, 9), request, content)
        content.update(
            {'vacancies_list': html_vacancies,
             "empty_message": "Вакансий пока не зарегистрировано"})
        return render_to_response('vacancies/vacancies_page.html', content)

    # build template with/without possibility to send feedback
    # for each vacancy it rendered own html
    def build_vacancies_html_list(self, vacancies, request, context):
        user = request.user
        if user.is_anonymous():
            return self.build_anon_version(vacancies, context)
        else:
            return self.build_another_version(user, vacancies, context)

    # in case of user is not anonymous user can be one of few types
    # each one of types has own html_template
    def build_another_version(self, user, vacancies, context):
        template_list = []
        for vacancy in vacancies:
            rendered_vacancy = self.vacancy_html_factory(user, vacancy, context)
            template_list.append(rendered_vacancy)
        return template_list

    # if user is anonymous_user it build all vacancies_box with the same template
    # like: "you can voting but register yourself first"
    # and return it as list for context
    @staticmethod
    def build_anon_version(vacancies, context):
        template_list = []
        for vacancy in vacancies:
            # in case of button click it's redirected on registration page
            context.update({'vacancy': vacancy, 'redirect_page': '/users/registry'})
            rendered_vacancy = get_template("vacancies/single_list_element/not_marked.html").render(context)
            template_list.append(rendered_vacancy)
        return template_list

    # return one of vacancy_element_styles depending on the user
    # as html
    # each vacancy render own html_box and return it in list
    @classmethod
    def vacancy_html_factory(cls, user, vacancy, context):
        context.update({"vacancy": vacancy})

        if cls.is_member(user, vacancy):
            return get_template("vacancies/single_list_element/member.html").render(context)
        if cls.is_not_voted(user, vacancy):
            return get_template("vacancies/single_list_element/not_marked.html").render(context)
        # if is voted early
        return get_template("vacancies/single_list_element/marked.html").render(context)

    @staticmethod
    def is_not_voted(user, vacancy):
        return vacancy.is_unique_feedback_with(user)

    @staticmethod
    def is_member(user, vacancy):
        return user in vacancy.project.members.all()


class VacancyRegistrationView(CustomView):
    def get(self, request, *args, **kwargs):
        form = VacancyRegistrationForm()
        return render_to_response('vacancies/vacancy_form.html', self.render_context(form, request))

    def post(self, request, *args, **kwargs):
        fill_form = VacancyRegistrationForm(request.POST or None, request.FILES)
        project = Project.get_by_name(request.GET['groupName'])
        if fill_form.try_save_vacancy(request.user, project):
            return JsonResponse(self.json_answer_if_success())
        else:
            return JsonResponse(self.json_answer_if_fail(request, fill_form))

    @staticmethod
    def render_context(form, request):
        group_name = request.GET['groupName']
        c = {'form': form,
             'replace_to_url': UrlKeeper.render_group_bank_url(group_name),
             'success_message': "Форма успешно создана и добавлена в поиск," +
                                " вы можете изменить ее в любое время в вашем кабинете",
             'registration_title': 'Создать новую вакансию'}
        c.update(csrf(request))
        return c


class VacancyEditView(CustomView):
    def get(self, request, *args, **kwargs):
        edit_form = VacancyRegistrationForm(instance=self.get_vacancy(request))
        return render_to_response('vacancies/vacancy_form.html', self.render_context(edit_form, request))

    def post(self, request, *args, **kwargs):
        old_vacancy = self.get_vacancy(request)
        fill_form = VacancyRegistrationForm(request.POST or None,instance=old_vacancy)
        modified_project = self.get_vacancy(request).project
        if modified_project.is_admin(request.user):
            if fill_form.try_edit():
                return JsonResponse(self.json_answer_if_success())
        return JsonResponse(self.json_answer_if_fail(request, fill_form))

    def get_vacancy(self, request):
        return Vacancy.get_by_id(request.GET['vacancyId'])

    def render_context(self, form, request):
        group_name = self.get_vacancy(request).project.name
        c = {'form': form,
             'replace_to_url': UrlKeeper.render_group_bank_url(group_name),
             'success_message': "Форма успешно изменена",
             'registration_title': 'Изменить вакансию'}
        c.update(csrf(request))
        return c


# handler for feedback
class FeedbackIncrementHandler(View):
    def get(self, request, *args, **kwargs):
        vacancy = Vacancy.get_by_id(request.GET['vacancyId'])
        answering_user = request.user

        if self.is_allowed_to_feedback(answering_user, vacancy):
            RelationToFeedback.objects.create(vacancy=vacancy, member=answering_user)
            self.send_link_to_project_mail(answering_user, vacancy.project, request)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    @staticmethod
    def send_link_to_project_mail(answering_user, project, request):
        project_mail = project.get_admin().email
        user_cabin = UrlKeeper.render_full_user_bank(answering_user.username, request)
        send_mail("Отклик на вакансию",
                  "На вашу вакансию откликнулся пользователь: %s.Вы можете связаться с ним по почте: %s,"
                  "или ознакомиться с его личным кабинетом: %s" %
                  (answering_user.username, answering_user.email, "http://" + user_cabin),
                  EMAIL_HOST,
                  [project_mail], fail_silently=False)

    @staticmethod
    def is_allowed_to_feedback(user, vacancy):
        return not user.is_anonymous() \
               and not vacancy.project.is_member(user) \
               and vacancy.is_unique_feedback_with(user)


# load list of users which press to "feed back"
# in group cabin
class FeedersListLoader(View):
    def get(self, request, *args, **kwargs):
        vacancy = Vacancy.get_by_id(request.GET['vacancyId'])
        admin_of_group = request.user
        group = vacancy.project
        if group.is_admin(admin_of_group):
            return JsonResponse({'success': True, 'content': self.build_content(vacancy, request)})
        else:
            return JsonResponse({'success': False})

    @staticmethod
    def build_content(vacancy, request):
        context = get_static_context(request.user)
        context.update({'members': RelationToFeedback.get_members_by_vacancy(vacancy)})
        return get_template('projects/components/show_feedback_to_vacancy.html').render(context)
