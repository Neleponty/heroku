# coding=utf8
from crispy_forms.utils import render_crispy_form
from django.contrib.auth import authenticate, login, get_backends, logout
from django.template.context_processors import csrf
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.views.generic import View
from apps.users.models import StudentRegistrationForm, StudentLoginForm, Student, StudentEditForm
from stpProject.static import get_static_context
from apps.vacancies.models import RelationToFeedback

# all forms which process of this method should override save_form
from apps.projects.models import Membership


def save_post_form(form, request):
    if form.is_valid():
        form.save_form(form, request)
        return {'success': True}
    # in case of mistake send fill form
    c = {}
    c.update(csrf(request))
    form_html = render_crispy_form(form, context=c)
    return {'success': False, 'form_html': form_html}


class UserCabinLoader(View):
    """
        Handler of user account requests
        in case if user in session is owner, then return template to owner version
        else return alien version of page
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        member = Student.get_by_name(request.GET['userName'])
        user_is_cabin_owner = self.compare_strings(self, request.GET["userName"], user.username)
        # when user go to own cabin it true
        # when other member want to watch someone else cabin it false
        if user.is_authenticated() & user_is_cabin_owner:
            return self.build_page(member, user, 'user/user_cabin.html')
        else:
            return self.build_page(member, user, 'user/user_cabin_invasion.html')

    # context composing
    @staticmethod
    def build_page(member, user, template):
        c = get_static_context(user)
        c.update({
            "memberships": Membership.get_all_relations_by_member(member),
            "vacancies": RelationToFeedback.get_vacancies_by_member(member),
            "cabin_owner": member,
        })
        result = render_to_response(template, c)
        return result

    # hint to compare two strings in different coding
    @staticmethod
    def compare_strings(self, first_string, second_string):
        if len(first_string) != len(second_string):
            return False
        return self.__char_by_char(first_string, second_string)

    @staticmethod
    def __char_by_char(first_string, second_string):
        index = 0
        for letter in first_string:
            if letter != second_string[index]:
                return False
            index += 1
        return True


class UserRegistration(View):
    def get(self, request, *args, **kwargs):
        c = {"form": StudentRegistrationForm, "registration_title": "Регистрация пользователя",
             "success_message": "Регистрация успешно завершена", 'replace_to_url': '/'}
        c.update(csrf(request))
        return render_to_response('../templates/registration/registration_form.html', c)

    def post(self, request, *args, **kwargs):
        filled_form = StudentRegistrationForm(request.POST or None, request.FILES, request)
        return JsonResponse(save_post_form(filled_form, request))


class UserAccountEdit(View):
    def get(self, request, *args, **kwargs):
        c = {"form": StudentEditForm(instance=request.user),
             "registration_title": "Изменение данных пользователя",
             "success_message": "Данные изменены", 'replace_to_url': '/'}
        c.update(csrf(request))
        return render_to_response('../templates/registration/registration_form.html', c)

    def post(self, request, *args, **kwargs):
        filled_form = StudentEditForm(request.POST or None, request.FILES)
        return JsonResponse(save_post_form(filled_form, request))


class UserLogin(View):
    def get(self, request, *args, **kwargs):
        c = {"form": StudentLoginForm, "registration_title": "Вход", 'success_message': "Вы вошли",
             'replace_to_url': '/'}
        c.update(csrf(request))
        return render_to_response('../templates/registration/login_form.html', c)

    def post(self, request, *args, **kwargs):
        return JsonResponse(self.login_process(request))

    @staticmethod
    def login_process(request):
        get_backends()
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return {'success': True}
        c = {}
        c.update(csrf(request))
        form_html = render_crispy_form(StudentLoginForm(), context=c)
        return {'success': False, 'form_html': form_html}


class UserLogout(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_active:
            logout(request)
        c = {"logout_message": "Вы вышли"}
        c.update(csrf(request))
        return render_to_response('registration/logout_page.html', c)
