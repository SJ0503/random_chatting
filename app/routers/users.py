from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.utils.send_email import send_email
from app.config import settings
import requests


router = APIRouter()

KAKAO_TOKEN_URL = settings.kakao_token_url
KAKAO_USERINFO_URL = settings.kakao_userInfo_url
KAKAO_CLIENT_ID = settings.kakao_client_url
REDIRECT_URI = settings.redirect_url
KAKAO_AUTH_URL = settings.kakao_auth_url

# print(settings)

# ✅ JWT 설정
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/login")
def login(data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    ✅ 이메일 & 카카오 로그인 처리
    """
    # print(data)
    if data.login_type == "email":
        # ✅ 이메일 로그인 처리
        user = db.query(models.User).filter(models.User.user_email == data.email).first()
        if not user or not auth.verify_password(data.password, user.user_password):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    elif data.login_type == "kakao":
        # print("kakao로그인 처리 실행", KAKAO_TOKEN_URL)
        # ✅ 카카오 로그인 처리
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

        kakao_id = str(user_info.get("id"))  # 카카오 ID를 문자열로 변환
        if not kakao_id:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")

        # ✅ DB에서 카카오 사용자 확인
        user = db.query(models.User).filter(models.User.user_kakao_id == kakao_id).first()
        if not user:
            return {"isNewUser": True, "kakao_id": kakao_id}  # 신규 사용자 → 회원가입 진행

 # ✅ JWT + Refresh Token 발급
    access_token = auth.create_access_token(data={"sub": user.user_id, "nickname": user.user_nickname})
    refresh_token = auth.create_refresh_token(data={"sub": user.user_id})

    # ✅ Refresh Token을 HTTP-Only Cookie에 저장
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS 환경에서만 쿠키 전송 (개발 단계에서는 False로 테스트 가능)
        samesite="Lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7일 유지
    )

    return {
        "accessToken": access_token,
        "user": {
            "user_id": user.user_id,
            "user_email":user.user_email,
            "nickname": user.user_nickname,
            "age": user.user_age,
            "gender": user.user_gender,
            "region": user.user_region,
            "type": user.user_login_type
            
        }
    }

@router.post("/logout")
def logout(response: Response):
    """
    ✅ 로그아웃: Refresh Token 쿠키 제거
    """
    response.delete_cookie("refresh_token")
    return {"message": "로그아웃되었습니다."}


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
    user_region=user.user_region,
    user_login_type="email"
)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/refresh-token")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    ✅ Refresh Token을 사용하여 새로운 Access Token 발급
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

    # ✅ 리프레시 토큰 검증
    payload = auth.verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # ✅ 새 Access Token 발급
    new_access_token = auth.create_access_token(data={"sub": user.user_id, "nickname": user.user_nickname})

    return {"accessToken": new_access_token}


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
