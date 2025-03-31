# app/tasks/delete_users.py

from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
from celery import shared_task
from pytz import timezone
from sqlalchemy.orm import Session

kst = timezone("Asia/Seoul")

@shared_task(name="app.tasks.delete_users.delete_inactive_users")
def delete_inactive_users():
    db: Session = SessionLocal()
    try:
        # 함수 실행 시점 기준 현재 시간 계산
        now_kst = datetime.now(kst).replace(tzinfo=None)

        threshold = now_kst - timedelta(days=1)  # 테스트용 2분
        users_to_delete = db.query(models.User).filter(
            models.User.user_delete_time != None,
            models.User.user_delete_time <= threshold
        ).all()

        count = len(users_to_delete)

        for user in users_to_delete:
            db.delete(user)
        db.commit()

        print(f"✅ 삭제된 유저 수: {count}")
    except Exception as e:
        print("🔥 유저 삭제 중 에러:", e)
    finally:
        db.close()

