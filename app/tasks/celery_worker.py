# app/tasks/celery_worker.py

from celery import Celery
from app.config import settings
from celery.schedules import crontab

# 💡 반드시 태스크 모듈 import (등록 위해)
from app.tasks import delete_users  # 이거 빠지면 워커가 태스크 등록 못함

celery = Celery(
    "tasks",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)

celery.conf.timezone = 'Asia/Seoul'

celery.conf.beat_schedule = {
    'delete-inactive-users-every-day': {
        'task': 'app.tasks.delete_users.delete_inactive_users',
        'schedule': crontab(minute=0),  # 매 정시에 실행
    },
}
