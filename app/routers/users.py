from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from app import models, schemas, auth
from app.database import get_db
from app.utils.send_email import send_email
from app.config import settings

router = APIRouter()

KAKAO_TOKEN_URL = settings.kakao_token_url
KAKAO_USERINFO_URL = settings.kakao_userInfo_url
KAKAO_CLIENT_ID = settings.kakao_client_url
REDIRECT_URI = settings.redirect_url


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


# ✅ 카카오 로그인 엔드포인트
@router.post("/kakao/token")
def kakao_login(data: schemas.KakaoTokenRequest, db: Session = Depends(get_db)):
    token_response = requests.post(
        KAKAO_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code": data.code,
        },
    ).json()

    if "access_token" not in token_response:
        raise HTTPException(status_code=400, detail="카카오 인증 실패")

    access_token = token_response["access_token"]

    # ✅ 카카오 사용자 정보 요청
    user_info = requests.get(
        KAKAO_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    kakao_id = user_info.get("id")
    if not kakao_id:
        raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")

    # ✅ DB에서 사용자 존재 여부 확인
    existing_user = db.query(models.User).filter(models.User.user_kakao_id == kakao_id).first()

    if existing_user:
        return {"isNewUser": False, "accessToken": access_token}

    return {"isNewUser": True, "accessToken": access_token, "kakao_id": kakao_id}


# ✅ 카카오 회원가입 엔드포인트
@router.post("/kakao/register", response_model=schemas.UserResponse)
def register_kakao_user(user: schemas.KakaoRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.user_kakao_id == user.user_kakao_id).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 사용자입니다.")

    new_user = models.User(
        user_kakao_id=user.user_kakao_id,
        user_nickname=user.user_nickname,
        user_gender=user.user_gender,
        user_age=user.user_age,
        user_region=user.user_region,
        user_password=None  # 카카오는 비밀번호 없음
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


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
