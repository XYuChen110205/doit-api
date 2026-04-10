"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import UserCreate, UserLogin, User, Token, UserUpdate
from app.services.auth_service import (
    create_user, authenticate_user, create_access_token, 
    verify_token, get_user_by_username, update_user
)
from app.response import success, error

router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        created_at=user.created_at
    )


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """用户注册"""
    try:
        user = await create_user(user_data)
        access_token = create_access_token(data={"sub": user.username})
        return success(data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        })
    except HTTPException as e:
        return error(message=e.detail, code=e.status_code)
    except Exception as e:
        return error(message=f"注册失败: {str(e)}", code=500)


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """用户登录"""
    try:
        user = await authenticate_user(login_data)
        if not user:
            return error(message="用户名或密码错误", code=401)
        
        access_token = create_access_token(data={"sub": user.username})
        return success(data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar,
                "created_at": user.created_at
            }
        })
    except Exception as e:
        return error(message=f"登录失败: {str(e)}", code=500)


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return success(data=current_user)


@router.put("/me", response_model=dict)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新当前用户信息"""
    try:
        updated_user = await update_user(current_user.id, update_data.dict(exclude_unset=True))
        return success(data=updated_user)
    except HTTPException as e:
        return error(message=e.detail, code=e.status_code)
    except Exception as e:
        return error(message=f"更新失败: {str(e)}", code=500)


@router.post("/change-password", response_model=dict)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    from app.services.auth_service import verify_password, get_password_hash
    
    try:
        # 获取完整用户信息
        user_in_db = await get_user_by_username(current_user.username)
        if not user_in_db:
            return error(message="用户不存在", code=404)
        
        # 验证旧密码
        if not verify_password(old_password, user_in_db.hashed_password):
            return error(message="旧密码错误", code=400)
        
        # 更新密码
        from app.database import database
        query = """
            UPDATE users 
            SET hashed_password = :hashed_password, updated_at = :updated_at
            WHERE id = :id
        """
        await database.execute(query, {
            "id": current_user.id,
            "hashed_password": get_password_hash(new_password),
            "updated_at": __import__('datetime').datetime.utcnow()
        })
        
        return success(message="密码修改成功")
    except Exception as e:
        return error(message=f"修改密码失败: {str(e)}", code=500)
