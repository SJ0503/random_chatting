from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 비밀번호 해싱
    hashed_password = auth.hash_password(user.user_password)

    # 사용자 생성
    new_user = models.User(
        user_nickname=user.user_nickname,
        user_email=user.user_email,
        user_password=hashed_password,
        user_gender=user.user_gender,
        user_age=user.user_age,
        user_region=user.user_region
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # db에 저장된 새 사용자 반환

    return new_user

@router.get("/check-nickname")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user_nickname = db.query(models.User).filter(models.User.user_nickname == nickname).first()
    if existing_user_nickname:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다")
    return {"message": "사용 가능한 닉네임입니다"}
