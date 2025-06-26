from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..config import settings
from redis import Redis



DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db():
    async with async_session_factory() as session:
        yield session

# Redis client
redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)