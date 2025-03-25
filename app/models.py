from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class LoginType(str, enum.Enum):
    email = "email"
    kakao = "kakao"

class User(Base):
    __tablename__ = "users"  # 테이블 이름

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # PK
    user_email = Column(String(255), unique=True, index=True, nullable=True)  # 이메일 (고유값, NULL 허용)
    user_nickname = Column(String(50), unique=True, index=True, nullable=False)  # 닉네임 (고유값, NOT NULL)
    user_age = Column(Integer, nullable=True)  # 나이 (NULL 허용)
    user_gender = Column(String(10), nullable=True)  # 성별 (NULL 허용)
    user_region = Column(String(100), nullable=True)  # 거주 지역 (NULL 허용)
    user_password = Column(String(255), nullable=True)  # 비밀번호 (NULL 허용)
    user_is_active = Column(Boolean, default=True)  # 계정 활성화 상태 (기본값: True)
    user_created_at = Column(DateTime, server_default=func.now())  # 계정 생성 시간 (기본값: 현재 시간)
    user_updated_at = Column(DateTime, onupdate=func.now())  # 계정 수정 시간 (자동 갱신)
    user_last_login = Column(DateTime, default=None)  # 마지막 로그인 시간 (NULL 허용)
    user_kakao_id = Column(String(255), unique=True, nullable=True)  # 카카오 계정 고유 ID (고유값, NULL 허용)
    user_login_type = Column(Enum(LoginType), nullable=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, user_email={self.user_email}, user_nickname={self.user_nickname})>"
