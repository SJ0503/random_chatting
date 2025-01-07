from sqlalchemy import create_engine  # SQLAlchemy에서 데이터베이스 엔진을 생성하기 위한 모듈
from sqlalchemy.orm import declarative_base  # ORM 모델의 베이스 클래스를 생성하기 위한 모듈
from sqlalchemy.orm import sessionmaker  # 데이터베이스 세션을 생성하고 관리하기 위한 모듈
from decouple import Config  # 환경 변수(.env 파일)에서 값을 가져오기 위한 라이브러리

# .env 파일에서 설정을 읽어오는 Config 객체 생성
config = Config(".env")

# .env 파일에서 DATABASE_URL 값을 가져오기
# DATABASE_URL은 데이터베이스 연결 정보 (예: MySQL, PostgreSQL, SQLite 등)를 포함합니다.
# 예: mysql+mysqlconnector://username:password@host:port/database
DATABASE_URL = config("DATABASE_URL")

# 데이터베이스 연결 엔진 생성
# create_engine은 SQLAlchemy의 핵심 객체로, 데이터베이스와의 실제 연결을 처리합니다.
# DATABASE_URL은 데이터베이스 종류, 드라이버, 사용자 이름, 비밀번호, 호스트, 포트, 데이터베이스 이름 등을 포함합니다.
engine = create_engine(DATABASE_URL)

# 데이터베이스 세션 생성기(sessionmaker) 생성
# SessionLocal은 데이터베이스와 상호작용할 수 있는 세션 객체를 생성하는 팩토리입니다.
# - autocommit=False: 자동으로 커밋하지 않음. 작업이 완료된 후 명시적으로 커밋해야 함.
# - autoflush=False: 세션에서 데이터를 플러시(데이터베이스에 반영)하지 않음.
# - bind=engine: 생성된 엔진을 세션에 연결하여 데이터베이스와 통신 가능하게 함.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy ORM 모델의 베이스 클래스 생성
# declarative_base()는 모든 데이터베이스 모델 클래스가 상속받아야 할 기본 클래스입니다.
# 이 클래스는 테이블과 Python 클래스 간의 매핑을 정의합니다.
Base = declarative_base()

# 데이터베이스 세션을 관리하는 함수 정의
# get_db 함수는 FastAPI에서 의존성 주입(Dependency Injection)으로 사용됩니다.
def get_db():
    # SessionLocal()을 호출하여 데이터베이스와의 세션을 생성합니다.
    db = SessionLocal()
    try:
        # yield를 사용해 생성된 세션 객체를 반환합니다.
        # FastAPI 라우트에서 사용자가 데이터베이스 작업을 수행할 수 있도록 세션을 제공.
        yield db
    finally:
        # 작업이 끝난 후 세션을 닫아 데이터베이스 리소스를 해제합니다.
        db.close()
