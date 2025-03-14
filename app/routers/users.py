from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.utils.send_email import send_email

router = APIRouter()

# ✅ 이메일 회원가입 엔드포인트
@router.post("/register", response_model=schemas.UserResponse)
def register_email_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.hash_password(user.user_password)

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
    db.refresh(new_user)

    return new_user

# ✅ 로그인 엔드포인트
@router.post("/login")
def check_email(email: str, db: Session = Depends(get_db)):
    existing_user_email = db.query(models.User).all(models.User.user_email == email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="이미 존재하는 이멜입니다다")
    # t수정합시다 이거 아닙니다.
    return existing_user_email


# ✅ 이메일 인증번호 전송 엔드포인트
@router.post("/send-verification-code")
def send_verification_code(email: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.user_email == email).first()
    if existing_user:
        return {"message": "이미 등록된 이메일입니다."}

    verification_code = auth.generate_verification_code(email)

    send_email(
        to_email=email,
        subject="이메일 인증번호",
        body=f"MyChat 인증번호는 {verification_code}입니다. 5분 내에 입력해주세요."
    )

    return {"message": "인증번호가 이메일로 전송되었습니다"}


# ✅ 이메일 인증번호 검증 엔드포인트
@router.post("/verify-code")
def verify_code(email: str, code: str):
    if not auth.verify_code(email, code):
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다")
    return {"message": "인증 성공"}


# ✅ 닉네임 중복 확인 엔드포인트
@router.get("/check-nickname")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user_nickname = db.query(models.User).filter(models.User.user_nickname == nickname).first()
    if existing_user_nickname:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다")
    return {"message": "사용 가능한 닉네임입니다"}
