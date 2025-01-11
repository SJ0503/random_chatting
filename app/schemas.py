from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    user_nickname: str  # 닉네임
    user_email: Optional[EmailStr] = None  # 이메일 (선택사항)
    user_password: Optional[str] = None  # 비밀번호 (일반 회원가입 시 필요)
    user_gender: Optional[str] = None  # 성별 (선택사항)
    user_age: Optional[int] = None  # 나이 (선택사항)
    user_region: Optional[str] = None  # 거주 지역 (선택사항)
    user_kakao_id: Optional[str] = None  # 카카오 고유 ID (선택사항)

class UserResponse(BaseModel):
    user_id: int  # PK
    user_email: Optional[EmailStr] = None  # 이메일
    user_nickname: str  # 닉네임
    user_gender: Optional[str] = None  # 성별
    user_age: Optional[int] = None  # 나이
    user_region: Optional[str] = None  # 거주지
    user_created_at: Optional[datetime] = None  # 생성 시간
    user_last_login: Optional[datetime] = None  # 마지막 로그인 시간

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 Pydantic 모델로 변환
        orm_mode = True  # SQLAlchemy ORM 객체를 변환 가능하게 설정
