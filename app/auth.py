from passlib.context import CryptContext
import random
import string
import redis
from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends

# ✅ JWT 설정
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # 액세스 토큰 만료 시간 (30분)
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 리프레시 토큰 만료 시간 (7일)


# ✅ FastAPI 보안 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)

# ✅ JWT 액세스 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ JWT 리프레시 토큰 생성
def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

# ✅ JWT 토큰 검증
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None  

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
