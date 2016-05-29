from django.contrib.auth.models import User, UserManager
from django.db import models
from django.forms import ModelForm, Textarea
from django.forms.widgets import PasswordInput
from stpProject import static


class Student(User):
    GENDER_TYPES = (
        ('M', u'Мужской'),
        ('F', u'Женский'),
    )

    description = models.TextField('About you', max_length=500)
    gender = models.CharField(max_length=10, choices=GENDER_TYPES)
    avatar = models.FileField(max_length=300, blank=True)
    objects = UserManager()

    @staticmethod
    def get_by_name(name):
        return Student.objects.get(username=name)

    # top list query
    @staticmethod
    def get_by_bounds(bottom, top):
        return Student.objects.all()[bottom:top]

    @staticmethod
    def update(form, request):
        # todo: clean
        modified_student = form.save(commit=False)
        final_instance = request.user
        final_instance.first_name = modified_student.first_name
        final_instance.last_name = modified_student.last_name
        final_instance.email = modified_student.email
        final_instance.description = modified_student.description
        final_instance.gender = modified_student.gender
        final_instance.avatar = modified_student.avatar
        return final_instance


class StudentRegistrationForm(ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'description', 'gender', 'avatar']
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 2}),
            'password': PasswordInput(render_value=False)
        }

    def __init__(self, *args, **kwargs):
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Зарегистрировать")

    @classmethod
    def save_form(cls, form, request):
        form.save()


class StudentEditForm(ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'description', 'gender', 'avatar']
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 2}),
            'password': PasswordInput(render_value=False)
        }

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Поменять информацию")

    @classmethod
    def save_form(cls, form, request):
        updated_student = Student.update(form, request)
        updated_student.save()


class StudentLoginForm(ModelForm):
    class Meta:
        model = Student
        fields = ['username', 'password']
        widgets = {
            'password': PasswordInput(render_value=False)
        }

    def __init__(self, *args, **kwargs):
        super(StudentLoginForm, self).__init__(*args, **kwargs)
        static.crispy_form_init(self, u"Войти")
