from sqlmodel import SQLModel, Field, ForeignKey, Relationship, Column, text, Enum as SQLEnum
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from pydantic import EmailStr
from datetime import datetime
from typing import List 
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    SUPERUSER= "superuser"
    MEMBER= "member"

class UserDB(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID, primary_key=True))
    username: str = Field(sa_column=Column(pg.VARCHAR(50), unique=True, nullable=False))
    email: EmailStr = Field(sa_column=Column(pg.VARCHAR(60), unique=True, nullable=False))
    hashpassword: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False), exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")))
    last_seen: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")))
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, default=False))
    role : Role = Field(sa_column=Column(SQLEnum(Role), nullable=False, default=Role.MEMBER.value))
    taskdb: List["TaskDB"] = Relationship(back_populates="userdb")

class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"
    uid : UUID = Field(sa_column=Column(pg.UUID, ForeignKey("users.uid"), nullable=False))
    task_id: int = Field(sa_column=Column(pg.INTEGER, primary_key=True))
    title: str = Field(sa_column=Column(pg.VARCHAR(1000), nullable=False))
    content: str = Field(sa_column=Column(pg.VARCHAR(100000), nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")))
    is_done: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, default=False))
    verified: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, default=False))
    for_user: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False))    
    userdb: UserDB = Relationship(back_populates="taskdb")

