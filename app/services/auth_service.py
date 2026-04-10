"""认证服务"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from fastapi import HTTPException, status
from app.database import database
from app.models.user import UserCreate, UserLogin, UserInDB, User

# JWT 配置 - 简化版本，不使用 jose
SECRET_KEY = "your-secret-key-here-change-in-production"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # 简单的 SHA256 哈希验证
    salt, stored_hash = hashed_password.split('$')
    computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return secrets.compare_digest(computed_hash, stored_hash)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # 生成随机 salt
    salt = secrets.token_hex(16)
    # SHA256 哈希
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌 - 简化版本"""
    import base64
    import json
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire.isoformat()})
    
    # 简单的 base64 编码（生产环境应该使用 JWT）
    payload = json.dumps(to_encode).encode()
    return base64.b64encode(payload).decode()


def verify_token(token: str) -> Optional[str]:
    """验证令牌，返回用户名 - 简化版本"""
    import base64
    import json
    
    try:
        payload = base64.b64decode(token).decode()
        data = json.loads(payload)
        username = data.get("sub")
        
        # 检查是否过期
        exp_str = data.get("exp")
        if exp_str:
            exp = datetime.fromisoformat(exp_str)
            if datetime.utcnow() > exp:
                return None
        
        return username
    except Exception:
        return None


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """根据用户名获取用户"""
    query = "SELECT * FROM users WHERE username = :username"
    result = await database.fetch_one(query, {"username": username})
    if result:
        return UserInDB(**result)
    return None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """根据邮箱获取用户"""
    query = "SELECT * FROM users WHERE email = :email"
    result = await database.fetch_one(query, {"email": email})
    if result:
        return UserInDB(**result)
    return None


async def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """根据ID获取用户"""
    query = "SELECT * FROM users WHERE id = :id"
    result = await database.fetch_one(query, {"id": user_id})
    if result:
        return UserInDB(**result)
    return None


async def create_user(user_data: UserCreate) -> User:
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = await get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    query = """
        INSERT INTO users (username, email, hashed_password, created_at)
        VALUES (:username, :email, :hashed_password, :created_at)
        RETURNING id, username, email, avatar, created_at
    """
    values = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await database.fetch_one(query, values)
    return User(**result)


async def authenticate_user(login_data: UserLogin) -> Optional[UserInDB]:
    """认证用户"""
    user = await get_user_by_username(login_data.username)
    if not user:
        return None
    if not verify_password(login_data.password, user.hashed_password):
        return None
    return user


async def update_user(user_id: int, update_data: dict) -> User:
    """更新用户信息"""
    # 构建更新字段
    fields = []
    values = {"id": user_id, "updated_at": datetime.utcnow()}
    
    if "username" in update_data and update_data["username"]:
        # 检查新用户名是否已存在
        existing = await get_user_by_username(update_data["username"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        fields.append("username = :username")
        values["username"] = update_data["username"]
    
    if "email" in update_data and update_data["email"]:
        # 检查新邮箱是否已存在
        existing = await get_user_by_email(update_data["email"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        fields.append("email = :email")
        values["email"] = update_data["email"]
    
    if "avatar" in update_data:
        fields.append("avatar = :avatar")
        values["avatar"] = update_data["avatar"]
    
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有要更新的字段"
        )
    
    fields.append("updated_at = :updated_at")
    
    query = f"""
        UPDATE users 
        SET {', '.join(fields)}
        WHERE id = :id
        RETURNING id, username, email, avatar, created_at
    """
    
    result = await database.fetch_one(query, values)
    return User(**result)
