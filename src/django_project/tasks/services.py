from django.db import transaction
from .models import TaskQueue

def fetch_task():
    with transaction.atomic():
        task = TaskQueue.objects.select_for_update(skip_locked=True).filter(status='pending').first()
        if task:
            task.status = 'in_progress'
            task.save()
            return task
    return None
