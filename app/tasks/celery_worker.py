from celery import Celery
from app.config import settings
from celery.schedules import crontab


celery = Celery(
    "tasks",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)

celery.conf.timezone = 'Asia/Seoul'

# celery.conf.beat_schedule = {
#     'delete-inactive-users-every-day': {
#         'task': 'app.tasks.delete_users.delete_inactive_users',
#         'schedule': crontab(minute=30, hour=23),  # 매일 00:00에 실행
#     },
# }

celery.conf.beat_schedule = {
    'delete-inactive-users-every-day': {
        'task': 'app.tasks.delete_users.delete_inactive_users',
        'schedule': crontab(minute='*/1')  # 매 1분마다 실행

    },
}

