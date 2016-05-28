import datetime
from django.db.models.signals import post_init
from django.dispatch import receiver
from apps.projects.models import Project
from apps.projects.models import TEAM_STATUS
from apps.vacancies.models import Vacancy


# this signal will called after Project __init__
@receiver(post_init, sender=Project)
def check_status_end_edit(**kwargs):
    instance = kwargs['instance']
    if instance.status == TEAM_STATUS['Start']:
        return
    is_released = instance.status is not TEAM_STATUS['Released'] and instance.release_date <= datetime.date.today()
    if is_released:
        instance.finish_project()
        return
    has_any_vacancies = Vacancy.get_vacancies_by_project(instance).count > 0
    if has_any_vacancies:
        instance.status = TEAM_STATUS['Find']
