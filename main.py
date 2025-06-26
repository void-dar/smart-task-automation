from fastapi import FastAPI
from .routes.user import login_service
from .routes.tasks import task_router
from contextlib import asynccontextmanager
from .db.main import init_db, engine
from sqlmodel import text
from slowapi import _rate_limit_exceeded_handler
from .utilities.utils import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
  
    try:
        print("server is starting")
        await init_db()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print("connection established")
    except Exception as e:
        print(f"Connection failed: {e}")

    yield
    print("Server shutting down....")
    await engine.dispose()
    print("Server shut down")


app = FastAPI(
    title="Task Manager app",
    description="A simple task manager API",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)


app.include_router(login_service, prefix="/api/auth", tags=["UserAuth"])
app.include_router(task_router, prefix="/api/app", tags=["Task Service"])