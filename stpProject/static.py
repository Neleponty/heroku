from django.template.loader import get_template
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class UrlKeeper:
    """
        Hold a urls which load on each page
    """

    @staticmethod
    def render_group_bank_url(name):
        return UrlKeeper.KeyUrlPairs["GroupByName"] + name

    @staticmethod
    def render_user_bank_url(name):
        return UrlKeeper.KeyUrlPairs["UserByName"] + name

    @staticmethod
    def render_full_user_bank(name, request):
        return request.META['HTTP_HOST'] + UrlKeeper.render_user_bank_url(name)

    @staticmethod
    def render_full_group_bank(name, request):
        return request.META['HTTP_HOST'] + UrlKeeper.render_group_bank_url(name)

    KeyUrlPairs = {
        "GroupByName": "/group/GroupBank?groupName=",
        "UserByName": "/users/UserBank?userName=",
        "VacanciesId": "?vacancyId="
    }


def get_static_context(user):
    """
    all pages has this variables exclude registration pages
    all links to user/group/resources in page must be processed by Bank's View
    :param user: user from session in request
    :return: piece of context to template
    """
    user_bank = UrlKeeper.KeyUrlPairs["UserByName"]
    out_context = {
        "user": user,
        "GroupBank": UrlKeeper.KeyUrlPairs["GroupByName"],
        "UserBank": user_bank,
        "VacanciesId": UrlKeeper.KeyUrlPairs["VacanciesId"],
        "right_bar_template": build_right_bar(user),
        "empty_message": "Не зарегистрировано ни одной группы"
    }
    # build menu template
    out_context.update({"NavBar": build_menu(user, {'UserBank': user_bank, 'user': user})}, )
    return out_context


def build_menu(user, c):
    if user.is_authenticated():
        return get_template('titlePage/identified_user_menu.html').render(c)
    else:
        return get_template('titlePage/unnamed_user_menu.html').render()


def build_right_bar(user):
    if user.is_authenticated():
        return get_template('titlePage/identified_user_right_bar.html').render({'user': user})
    else:
        return get_template('titlePage/unnamed_user_right_bar.html').render({'user': user})


'''
 each registration_form with crispy_forms_frontend must build with it
 '''


def crispy_form_init(self, submit_button_name):
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.form_action = ''
    self.helper.add_input(Submit('submit', submit_button_name))
    self.helper.attrs = {"enctype": "multipart/form-data"}
