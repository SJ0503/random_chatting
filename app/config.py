from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    redis_host: str
    redis_port: int
    kakao_token_url : str
    kakao_userInfo_url : str
    kakao_client_url : str
    redirect_url : str
    kakao_auth_url : str


    class Config:
        env_file = ".env"

settings = Settings()
