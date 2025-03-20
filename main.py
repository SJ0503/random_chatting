from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, kakao_users
import os

# FastAPI 앱 생성
app = FastAPI()

# 환경 변수에서 허용된 origin 가져오기 (배포 환경 대비)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 라우터 등록
app.include_router(users.router)
app.include_router(kakao_users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
