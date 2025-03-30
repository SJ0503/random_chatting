from app.tasks.celery_worker import celery
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta

@celery.task
def delete_inactive_users():
    db = SessionLocal()
    try:
        deadline = datetime.utcnow() - timedelta(minutes=2)
        users_to_delete = db.query(models.User).filter(
            models.User.user_delete_time != None,
            models.User.user_delete_time < deadline
        ).all()

        for user in users_to_delete:
            print(f"🧹 삭제됨: {user.user_email}")
            db.delete(user)

        db.commit()
    finally:
        db.close()
