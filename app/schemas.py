from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ✅ 일반 회원가입 요청 스키마
class UserCreate(BaseModel):
    user_nickname: str  # 닉네임
    user_email: EmailStr  # 이메일 (일반 회원가입용)
    user_password: str  # 비밀번호 (일반 회원가입용)
    user_gender: str = None  # 성별 (선택사항)
    user_age: int = None  # 나이 (선택사항)
    user_region: str= None  # 거주 지역 (선택사항)

# ✅ 이메일 & 카카오 로그인 요청 스키마
class LoginRequest(BaseModel):
    login_type: str  # "email" 또는 "kakao"
    user_email: Optional[EmailStr] = None  # 이메일 로그인 시 사용
    user_password: Optional[str] = None  # 이메일 로그인 시 사용
    code: Optional[str] = None  # 카카오 로그인 시 사용 (인가 코드)

# ✅ JWT 토큰 응답 스키마
class TokenResponse(BaseModel):
    accessToken: str

# ✅ 카카오 회원가입 요청 스키마
class KakaoRegisterRequest(BaseModel):
    user_kakao_id: int  # 카카오 고유 ID (필수)
    user_nickname: str  # 닉네임 (필수)
    user_age: int = None  # 나이 (선택사항)
    user_gender: str = None  # 성별 (선택사항)
    user_region: str= None  # 거주 지역 (선택사항)

# ✅ 회원 정보 응답 스키마
class UserResponse(BaseModel):
    user_id: int  # PK (필수)
    user_kakao_id: Optional[int] = None  # 카카오 ID (선택)
    user_email: Optional[EmailStr] = None  # 이메일 (선택)
    user_nickname: str  # 닉네임 (필수)
    user_gender: Optional[str] = None  # 성별 (선택)
    user_age: Optional[int] = None  # 나이 (선택)
    user_region: Optional[str] = None  # 거주지 (선택)
    user_created_at: Optional[datetime] = None  # 생성 시간
    user_last_login: Optional[datetime] = None  # 마지막 로그인 시간
    user_last_logout : Optional[datetime] = None  # 마지막 로그인 시간
    user_kakao_id: Optional[int] = None  # 카카오 ID (선택)


# ✅ 회원정보 수정스키마
class UserUpdate(BaseModel):
    user_password: Optional[str] = None
    user_age: Optional[int] = None
    user_region: Optional[str] = None

    class Config:
        from_attributes = True  # SQLAlchemy ORM 객체를 Pydantic 모델로 변환


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str

