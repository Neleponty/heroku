# coding=utf8
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.db.models import Q
from django import forms
from django.forms import Form


class ProjectLightSearch(Form):
    text = forms.CharField(required=True)
    date = forms.DateField(required=False, label='Искать раньше даты')

    class Meta:
        fields = ['text', 'date']

    def __init__(self, *args, **kwargs):
        super(ProjectLightSearch, self).__init__(*args, **kwargs)
        # create and fill form params
        self.helper = FormHelper(self)
        crispy_form_init(self, 'Найти')
        self.helper.layout = Layout(
            Field('text', placeholder="Enter Email", autofocus=""),
            Field('date', placeholder="Enter Full Name"),
            Submit('sign_up', 'Найти', css_class="btn-warning"),
            )

    def search_lts_date(self, query):
        if self.date:
            return query.filter(pub_date__lte=self.date)
        else:
            return query

    def search_more_like(self, query):
        return query.filter(Q(title=self.text) | Q(title__contains=self.text))


class ProjectSearchForm(ProjectLightSearch):
    find_which_contain = forms.BooleanField(label='Искать ваши группы')
    find_which_not_contain = forms.BooleanField(label='Искать группы, в которых вас нет')

    def __init__(self, *args, **kwargs):
        super(ProjectSearchForm, self).__init__(*args, **kwargs)
        # create and fill form params
        self.helper = FormHelper()
        crispy_form_init(self, 'Найти')

    def get_projects_by_flags(self, user, membership_query):
        if self.find_which_contain:
            membership_query.filter(member=user)
        if self.find_which_not_contain:
            membership_query.exclude(member=user)

        result_projects = []
        for membership in membership_query:
            result_projects.append(membership.project)
        return result_projects


def crispy_form_init(self, submit_button_name):
    self.helper.form_method = 'post'
    self.helper.form_action = '/search/projects/'
    self.helper.add_input(Submit('submit', submit_button_name))
    self.helper.attrs = {"enctype": "multipart/form-data"}
    self.helper.render_unmentioned_fields = True