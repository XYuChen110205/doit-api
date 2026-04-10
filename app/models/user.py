"""用户模型"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import re


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """简单的邮箱格式验证"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v


class UserCreate(UserBase):
    """创建用户模型"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """简单的邮箱格式验证"""
        if v is not None and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v


class UserInDB(UserBase):
    """数据库用户模型"""
    id: int
    hashed_password: str
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型"""
    id: int
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None
