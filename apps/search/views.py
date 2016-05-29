# coding=utf8
from django.http import JsonResponse
from django.views.generic import View
from apps.projects.models import Membership, Project
from apps.search.forms import ProjectSearchForm, ProjectLightSearch
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form


# for anon_user
class ProjectLightView(View):
    def post(self, request, *args, **kwargs):
        search_request_form = ProjectLightSearch(request.POST)
        if search_request_form.is_valid():
            query_response = Project.objects.all()
            query_response = search_request_form.search_more_like(query_response)
            query_response = search_request_form.search_lts_date(query_response)
            return JsonResponse({'query': query_response})
        else:
            c = {}
            c.update(csrf(request))
            return JsonResponse({'form': render_crispy_form(search_request_form, c)})

    @staticmethod
    def update_context_light(context, request):
        c = {}
        c.update(csrf(request))
        form = ProjectLightSearch()
        context.update({'search_form': render_crispy_form(form, helper=form.helper, context=c)})
        return context


# for authenticated user
class ProjectSearchView(ProjectLightView):
    def post(self, request, *args, **kwargs):
        search_request_form = ProjectSearchForm(request.POST)

        # send list or message
        if search_request_form.is_valid():
            query_response = search_request_form.get_projects_by_flags(request.user, Membership.objects.all())
            query_response = search_request_form.search_more_like(query_response)
            query_response = search_request_form.search_lts_date(query_response)
            top_list_html = render_to_response('projects/groups_short_describe.html', {'shortGroups': query_response,})
            return JsonResponse({'result': top_list_html,
                                 'empty_message': 'По вашему запросу не найдено ни одного проекта'})
        else:
            c = {}
            c.update(csrf(request))
            return JsonResponse({'form': render_crispy_form(search_request_form, c)})

    # for main page loader
    @staticmethod
    def get_context_with_form(context, request):
        c = {}
        c.update(csrf(request))
        form = ProjectSearchForm()
        context.update({'search_form': render_crispy_form(form, helper=form.helper, context=c)}, )
        return context
