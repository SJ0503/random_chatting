from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from app import models, schemas
from app.database import get_db
from app.config import settings

router = APIRouter()

KAKAO_TOKEN_URL = settings.kakao_token_url
KAKAO_USERINFO_URL = settings.kakao_userInfo_url
KAKAO_CLIENT_ID = settings.kakao_client_url
REDIRECT_URI = settings.redirect_url
KAKAO_AUTH_URL = settings.kakao_auth_url


# ✅ 카카오 로그인 엔드포인트
@router.post("/kakao/token")
def kakao_login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
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
    print("🔴 받은 데이터:", user.dict())
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


@router.get("/kakao/login_url")
def get_kakao_login_url():
    """
    카카오 로그인 URL을 생성하여 프론트엔드로 전달
    """
    kakao_login_url = (
        f"{KAKAO_AUTH_URL}"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )

    return {"login_url": kakao_login_url}