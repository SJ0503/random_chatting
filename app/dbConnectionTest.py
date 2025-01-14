# from sqlalchemy import create_engine

# DATABASE_URL = "mysql+mysqlconnector://root:root@127.0.0.1:3306/chatting"

# engine = create_engine(DATABASE_URL)

# try:
#     connection = engine.connect()
#     print("MySQL 연결 성공!")
#     connection.close()
# except Exception as e:
#     print("MySQL 연결 실패:", e)

# import redis

# try:
#     client = redis.StrictRedis(host='localhost', port=6379, db=0)
#     response = client.ping()
#     if response:
#         print("Redis 연결 성공!")
# except redis.ConnectionError as e:
#     print(f"Redis 연결 실패: {e}")


from app.config import settings

# 환경 변수 값 출력
print("SMTP_SERVER:", settings.smtp_server)
print("SMTP_PORT:", settings.smtp_port)
print("SMTP_USER:", settings.smtp_user)
print("SMTP_PASSWORD:", settings.smtp_password)
print("REDIS_HOST:", settings.redis_host)
print("REDIS_PORT:", settings.redis_port)
print("DATABASE_URL:", settings.database_url)

import os

print("DATABASE_URL:", os.getenv("database_url"))
print("SMTP_SERVER:", os.getenv("smtp_server"))
print("SMTP_PORT:", os.getenv("smtp_port"))


