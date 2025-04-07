from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.utils.send_email import send_email
from app.config import settings
from app.dependencies import get_current_user
import requests
from datetime import datetime, timedelta
from pytz import timezone
kst = timezone("Asia/Seoul")
now_kst = datetime.now(kst).replace(tzinfo=None)

router = APIRouter()

KAKAO_TOKEN_URL = settings.kakao_token_url
KAKAO_USERINFO_URL = settings.kakao_userInfo_url
KAKAO_CLIENT_ID = settings.kakao_client_url
REDIRECT_URI = settings.redirect_url
KAKAO_AUTH_URL = settings.kakao_auth_url

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

@router.post("/login")
def login(data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):

    if data.login_type == "email":
        user = db.query(models.User).filter(models.User.user_email == data.user_email).first()
        if not user or not auth.verify_password(data.user_password, user.user_password):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    elif data.login_type == "kakao":
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

        user_info = requests.get(
            KAKAO_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_id = str(user_info.get("id"))
        if not kakao_id:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")

        user = db.query(models.User).filter(models.User.user_kakao_id == kakao_id).first()
        if not user:
            return {"isNewUser": True, "kakao_id": kakao_id}
        
    if user.user_delete_time:
            raise HTTPException(status_code=403, detail="탈퇴된 아이디 입니다. \n(탈퇴 시간 기준 24시간 후에 재가입 가능)")


    # ✅ 로그인 성공 시 마지막 로그인 시간 기록
    user.user_last_login = now_kst
    user.user_is_active = 1
    db.commit()

    access_token = auth.create_access_token(data={"sub": str(user.user_id), "nickname": user.user_nickname})
    refresh_token = auth.create_refresh_token(data={"sub": str(user.user_id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return {
        "accessToken": access_token,
        "user": {
            "user_id": user.user_id,
            "user_email": user.user_email,
            "nickname": user.user_nickname,
            "age": user.user_age,
            "gender": user.user_gender,
            "region": user.user_region,
            "type": user.user_login_type
        }
    }

@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # ✅ 현재 로그인된 사용자 가져오기
    user = db.query(models.User).filter(models.User.user_id == current_user.user_id).first()

    if user:
        user.user_is_active = 0
        user.user_last_logout = now_kst
        db.commit()

    response.delete_cookie("refresh_token")
    return {"message": "로그아웃되었습니다."}

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
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

    payload = auth.verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    new_access_token = auth.create_access_token(data={"sub": user.user_id, "nickname": user.user_nickname})

    return {"accessToken": new_access_token}

@router.post("/send-verification-code")
def send_verification_code(email: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.user_email == email).first()
    
       # ✅ 기존 탈퇴 사용자라면 24시간 제한 확인
    if existing_user:
        if existing_user.user_delete_time:
            time_since_deleted = now_kst - existing_user.user_delete_time
            if time_since_deleted< timedelta(days=1):
                print(timedelta)
                raise HTTPException(status_code=403, detail="탈퇴 후 24시간 이내에는 재가입할 수 없습니다.")
        else:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
        

    verification_code = auth.generate_verification_code(email)

    send_email(
        to_email=email,
        subject="이메일 인증번호",
        body=f"MyChat 인증번호는 {verification_code}입니다. 5분 내에 입력해주세요."
    )

    return {"message": "인증번호가 이메일로 전송되었습니다"}

@router.post("/verify-code")
def verify_code(email: str, code: str):
    if not auth.verify_code(email, code):
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다")
    return {"message": "인증 성공"}

@router.get("/check-nickname")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user_nickname = db.query(models.User).filter(models.User.user_nickname == nickname).first()
    if existing_user_nickname:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다")
    return {"message": "사용 가능한 닉네임입니다"}

@router.patch("/update-user")
def update_user(data: schemas.UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.user_id == current_user.user_id).first()

    if data.user_password:
        user.user_password = auth.hash_password(data.user_password)
    if data.user_age:
        user.user_age = data.user_age
    if data.user_region:
        user.user_region = data.user_region

    user.user_updated_at = now_kst
    db.commit()
    return {"message": "회원 정보가 수정되었습니다."}

@router.patch("/delete-user")
def delete_user(
    response: Response,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    ✅ 탈퇴 요청 → user_delete_time에 현재 시간 기록 + 리프레시 토큰 제거
    """
    if current_user.user_delete_time:
        raise HTTPException(status_code=400, detail="이미 탈퇴한 사용자입니다.")

    # ✅ 탈퇴 시간 기록
    current_user.user_delete_time = now_kst  # 또는 datetime.utcnow()

    db.commit()

    return {"message": "탈퇴 처리 완료 (24시간 이내 재가입 불가)"}

@router.post("/send-verification-code-for-findPW")
def send_verification_code(email: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.user_email == email).first()
    
       # ✅ 기존 탈퇴 사용자라면 24시간 제한 확인
    if existing_user:
        if existing_user.user_delete_time:
            time_since_deleted = now_kst - existing_user.user_delete_time
            if time_since_deleted< timedelta(days=1):
                print(timedelta)
                raise HTTPException(status_code=403, detail="탈퇴 진행중인 사용자 입니다.")
    else:
         raise HTTPException(status_code=400, detail="등록된 이메일이 아닙니다.")

    verification_code = auth.generate_verification_code(email)

    send_email(
        to_email=email,
        subject="비밀번호 재설정이메일 인증번호",
        body=f"MyChat 인증번호는 {verification_code}입니다. 5분 내에 입력해주세요."
    )

    return {"message": "인증번호가 이메일로 전송되었습니다"}

@router.patch("/reset-password")
def reset_password(data: schemas.PasswordReset, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="해당 이메일의 사용자가 존재하지 않습니다.")

    hashed_pw = auth.hash_password(data.new_password)
    user.user_password = hashed_pw
    user.user_updated_at = now_kst

    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
