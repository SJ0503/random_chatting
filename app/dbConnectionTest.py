from sqlalchemy import create_engine

DATABASE_URL = "mysql+mysqlconnector://root:root@127.0.0.1:3306/chatting"

engine = create_engine(DATABASE_URL)

try:
    connection = engine.connect()
    print("MySQL 연결 성공!")
    connection.close()
except Exception as e:
    print("MySQL 연결 실패:", e)