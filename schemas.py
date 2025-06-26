from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union
from .db.models import Role
from datetime import datetime
from uuid import UUID


class CreateUser(BaseModel):
    username: str = Field(min_length=2,max_length=50)
    email: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=50)
    role: Optional[Role] = Role.MEMBER.value

class LogIn(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=30)

class UserOut(BaseModel):
    uid: UUID
    username: str 
    email: EmailStr  
    created_at: Union[datetime, str]
    last_seen: Union[datetime, str]

class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    content: str = Field(min_length=1, max_length=100000)
    for_user: str = Field(min_length=1, max_length=50) 

class TaskOut(BaseModel):
    task_id: int
    title: str
    content: str
    created_at: datetime
    is_done: bool
    from_user: str

class UpdateTask(BaseModel):
    title: str = Field(max_length=1000)
    content: str = Field(max_length=100000)

class SelectFromName(BaseModel):
    username: str
    task_id: Union[int, None]

class Done(BaseModel):
    is_done: bool
    for_user: str

class Verify(BaseModel):
    verified: bool
    username: str
 
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: int

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
