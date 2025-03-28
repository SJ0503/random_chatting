from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
from pytz import timezone
kst = timezone("Asia/Seoul")
now_kst = datetime.now(kst).replace(tzinfo=None)

def delete_users_marked_for_deletion():
    db: Session = SessionLocal()

    cutoff_time = now_kst - timedelta(hours=24)

    users_to_delete = db.query(models.User).filter(
        models.User.user_delete_time != None,
        models.User.user_delete_time < cutoff_time
    ).all()

    for user in users_to_delete:
        print(f"Deleting user: {user.user_id}, 탈퇴 요청: {user.user_delete_time}")
        db.delete(user)

    db.commit()
    db.close()

if __name__ == "__main__":
    delete_users_marked_for_deletion()
