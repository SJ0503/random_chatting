from app.database import engine
from app import models
import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
models.Base.metadata.create_all(bind=engine)
print("테이블 생성 완료")