import datetime
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.encoding import smart_str
from django.views.generic import View
from stpProject.settings import MEDIA_ROOT


def rate_calculate():
    return 50


def date_across_days(days):
    return datetime.date.today() + datetime.timedelta(days=days)


class DocumentLoader(View):
    def get(self, request, *args, **kwargs):
        name = args[0]
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(name)
        response['X-Sendfile'] = smart_str(MEDIA_ROOT + '\\' + name)
        return response
