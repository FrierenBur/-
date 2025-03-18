from pydantic_settings import BaseSettings
from app.config.secret import WX_APP_ID,WX_APP_SECRET,JWT_SECRET_KEY

class Settings(BaseSettings):
    APP_ID: str = WX_APP_ID
    APP_SECRET: str = WX_APP_SECRET
    SECRET_KEY: str = JWT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./wechat_users.db"
    
    class Config:
        env_file = ".env"

settings = Settings()