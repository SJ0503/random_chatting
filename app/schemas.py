from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    user_nickname: str  # 닉네임
    user_email: Optional[EmailStr] = None  # 이메일 (선택사항)
    user_password: str  # 비밀번호
    user_gender: Optional[str] = None  # 성별 (선택사항)
    user_age: Optional[int] = None  # 나이 (선택사항)
    user_region: Optional[str] = None  # 거주지 (선택사항)

class UserResponse(BaseModel):
    user_id: int  # PK
    user_email: Optional[EmailStr] = None  # 이메일
    user_nickname: str  # 닉네임
    user_gender: Optional[str] = None  # 성별
    user_age: Optional[int] = None  # 나이
    user_region: Optional[str] = None  # 거주지
    user_created_at: Optional[str] = None  # 생성 시간
    user_last_login: Optional[str] = None  # 마지막 로그인 시간

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 Pydantic 모델로 변환 가능