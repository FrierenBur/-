import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config.config import settings
from app.models.User import User, get_db
from app.schemas.schemas import WechatLoginRequest, UserResponse, Token, UserInfo
from app.utils.auth import create_access_token, get_current_user

app = FastAPI(title="微信小程序登录API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/wx/login", response_model=Token)
async def login(request: WechatLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录接口
    """
    # 请求微信API获取openid和session_key
    url = f"https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.APP_ID,
        "secret": settings.APP_SECRET,
        "js_code": request.code,
        "grant_type": "authorization_code"
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    if "errcode" in result and result["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {result.get('errmsg', '未知错误')}"
        )
    
    openid = result.get("openid")
    session_key = result.get("session_key")
    
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="获取openid失败"
        )
    
    # 查找或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    
    if not user:
        # 创建新用户
        user = User(openid=openid, session_key=session_key)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 更新session_key
        user.session_key = session_key
        db.commit()
    
    # 如果提供了用户信息，则更新用户资料
    if request.user_info:
        update_user_info = {
            "nickname": request.user_info.get("nickName"),
            "avatar_url": request.user_info.get("avatarUrl"),
            "gender": request.user_info.get("gender"),
            "country": request.user_info.get("country"),
            "province": request.user_info.get("province"),
            "city": request.user_info.get("city")
        }
        
        for key, value in update_user_info.items():
            if value is not None:
                setattr(user, key, value)
        
        db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.openid}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/wx/user/me", response_model=UserResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return current_user

@app.put("/wx/user/update", response_model=UserResponse)
async def update_user_info(
    user_info: UserInfo,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息
    """
    for key, value in user_info.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)