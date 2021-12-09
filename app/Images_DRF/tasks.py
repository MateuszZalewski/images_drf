from celery import shared_task
from django.core.management import call_command


@shared_task
def delete_expired():
    call_command('delete_expired', )
