from passlib.context import CryptContext
import random
import string
import redis
from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta


# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=0)

def generate_verification_code(email: str) -> str:
    """
    이메일 인증번호 생성 및 저장
    """
    code = ''.join(random.choices(string.digits, k=6))
    redis_client.setex(f"verification:{email}", 300, code)  # 5분 유효
    return code

def verify_code(email: str, code: str) -> bool:
    """
    인증번호 검증
    """
    stored_code = redis_client.get(f"verification:{email}")
    if stored_code and stored_code.decode() == code:
        # 인증번호 삭제
        redis_client.delete(f"verification:{email}")
        redis_client.set(f"verified:{email}", "true", ex=3600)  # 1시간 인증 상태 유지
        return True
    return False

def is_email_verified(email: str) -> bool:
    """
    이메일 인증 상태 확인
    """
    return redis_client.get(f"verified:{email}") == b"true"

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)
