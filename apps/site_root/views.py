# coding=utf8
from django.shortcuts import render_to_response
from django.views.generic import View
from apps.projects.models import GROUP_CATEGORY, Project
from stpProject.static import get_static_context
from apps.search.views import ProjectSearchView, ProjectLightView


class HeadPageLoader(View):
    def get(self, request, *args, **kwargs):
        short_groups = Project.objects.all()
        context = get_static_context(request.user)
        context = build_top_list_content(0, 10, context)
        # context = self.update_by_user_auth(context, request)
        context.update({"shortGroups": short_groups,
                        "empty_message": "Не зарегистрировано ни одной Группы"})
        return render_to_response('home_page.html', context)

    def update_by_user_auth(self, context, request):
        if request.user.is_anonymous():
            return ProjectLightView.update_context_light(context, request)
        else:
            return ProjectSearchView.get_context_with_form(context, request)


# compose context to any pages which has a top list
def build_top_list_content(start, end, old_context):
    if old_context is not None:
        old_context.update({
            "types": GROUP_CATEGORY,  # варианты поиска по группам
            "bottom": start,
            "top": end,
        })
        return old_context

    return old_context
