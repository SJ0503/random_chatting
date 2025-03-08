from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.utils.send_email import send_email

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
    db.refresh(new_user)  # db에 저장된 새 사용자 반환환환환한환환

    return new_user



@router.post("/send-verification-code")
def send_verification_code(email: str, db: Session = Depends(get_db)):
    """
    이메일 인증번호 생성 및 전송
    """
    # 이메일 중복 확인
    existing_user = db.query(models.User).filter(models.User.user_email == email).first()
    if existing_user:
         return {"message": "이미 등록된 이메일입니다."}

    # 인증번호 생성
    verification_code = auth.generate_verification_code(email)

    # 이메일 전송
    send_email(
        to_email=email,
        subject="이메일 인증번호",
        body=f"Mychat 인증번호는 {verification_code}입니다. 5분 내에 입력해주세요."
    )

    return {"message": "인증번호가 이메일로 전송되었습니다"}

@router.post("/verify-code")
def verify_code(email: str, code: str):
    """
    인증번호 검증
    """
    if not auth.verify_code(email, code):
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다")
    return {"message": "인증 성공"}



@router.get("/check-nickname")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user_nickname = db.query(models.User).filter(models.User.user_nickname == nickname).first()
    if existing_user_nickname:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다")
    return {"message": "사용 가능한 닉네임입니다"}
