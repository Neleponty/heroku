# form for registration
from django.forms import Textarea, ModelForm
from apps.projects.models import Project, Event
from stpProject import static


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'title', 'category', 'describe', 'logo']
        widgets = {
            'describe': Textarea(attrs={'cols': 30, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Зарегистрировать проект")


# form for base information editing
class ProjectEditFoundationForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'describe', 'logo']
        widgets = {
            'describe': Textarea(attrs={'cols': 30, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectEditFoundationForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Поменять данные")


class ProjectEditEvent(ModelForm):
    class Meta:
        model = Event
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'cols': 20, 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectEditEvent, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Добавить событие")

    @classmethod
    def save_form(cls, fill_form, request):
        event = fill_form.save(commit=False)
        event.project = Project.get_by_name(request.GET['groupName'])
        event.save()
