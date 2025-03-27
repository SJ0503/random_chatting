from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_token
from app import models
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 정보가 없습니다.")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="토큰에서 사용자 ID를 찾을 수 없습니다.")

    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return user
