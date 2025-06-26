from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select, and_
from ..schemas import TaskIn, UpdateTask, Done, Verify
from ..db.models import TaskDB, UserDB
from ..db.main import AsyncSession, get_db
from ..utilities.jwt_handler import get_current_user
from ..utilities.checker import RoleChecker as c
from typing import Union

task_router = APIRouter()

@task_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task(data : TaskIn, db:AsyncSession = Depends(get_db), user: dict = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user.get("uid")
    statement = select(UserDB).where(UserDB.username == data.for_user)
    result = await db.exec(statement)
    result = result.first()
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username doesn't exist")
    statement = select(UserDB).where(data.for_user == UserDB.username)
    result = await db.exec(statement)
    result = result.first()
    if result is None or result is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username doesn't exist")
    if result.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't delegate task to another admin")
    try:
        new_task = TaskDB(uid=uid, title=data.title, content= data.content, for_user= data.for_user)
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        return new_task
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task creation failed")
    
@task_router.get("/tasks", status_code=status.HTTP_200_OK)
async def all_tasks(db:AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    uid = user["uid"]
    try:
        statement = select(TaskDB).where(uid == TaskDB.uid)
        result = await db.exec(statement)
        result = result.all()
        return result
    except:
        db.rollback()
       
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve tasks")
    
@task_router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def task_by_id(task_id:int , db:AsyncSession = Depends(get_db), user = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user["uid"]
    try:
        statement = select(TaskDB).where(and_(uid == TaskDB.uid, task_id == TaskDB.task_id))
        result = await db.exec(statement)
        result = result.first()
        return result
    except:
        db.rollback()
       
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve task")
    
@task_router.get("/tasks/{sent}/{task_id}", status_code=status.HTTP_200_OK)
async def user_tasks( sent: str, task_id: Union[int, None], db:AsyncSession = Depends(get_db), user = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user["uid"]
    if task_id != None:
        try:
            statement = select(TaskDB).where(and_(uid == TaskDB.uid, sent == TaskDB.for_user, task_id == TaskDB.task_id ))
            result = await db.exec(statement)
            result = result.all()
            return result
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve task")
    else:
        try:
            statement = select(UserDB).where(UserDB.username == sent)
            result = await db.exec(statement)
            result = result.first()
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
            statement = select(TaskDB).where(and_(uid == TaskDB.uid, sent == TaskDB.for_user))
            result = await db.exec(statement)
            result = result.all()
            return result
        except:
            db.rollback()
            
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve tasks")
    
    
@task_router.put("/tasks/{task_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_task(data:UpdateTask , task_id: int, db:AsyncSession = Depends(get_db), user = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user["uid"]
    try:
        statement = select(TaskDB).where(and_(uid == TaskDB.uid, task_id == TaskDB.task_id))
        result = await db.exec(statement)
        result = result.first()
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")

        result.title = data.title 
        result.content=data.content
        await db.commit()
        await db.refresh(result)

        return result
    except:
        db.rollback()
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update task")
        

@task_router.put("/tasks/done/{task_id}", status_code=status.HTTP_202_ACCEPTED)
async def task_done(data: Done, task_id: int, db:AsyncSession = Depends(get_db), user = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user["uid"]
    username = user["username"]
    try:
        statement = select(UserDB).where(UserDB.username == data.for_user)
        result = await db.exec(statement)
        result = result.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username doesn't exist")
        statement = select(TaskDB).where(and_(task_id == TaskDB.task_id, data.for_user == TaskDB.for_user, uid == TaskDB.uid))
        result = await db.exec(statement)
        result = result.first()
        result.is_done = data.is_done
        await db.commit()
        await db.refresh(result)

        return result
    except Exception as e:
        await db.rollback()
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update task")
    
@task_router.put("/tasks/verify/{task_id}", status_code=status.HTTP_202_ACCEPTED)
async def task_done(data: Verify, task_id: int, db:AsyncSession = Depends(get_db), user = Depends(get_current_user), role = Depends(c.check_role)):
    uid = user["uid"]
    
    try:
        statement = select(TaskDB).where(and_(task_id == TaskDB.task_id, data.username == TaskDB.for_user, uid == TaskDB.uid))
        result = await db.exec(statement)
        result = result.first()
        result.verified = data.verified
        await db.commit()
        await db.refresh(result)

        return result
    except:
        db.rollback()
  
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update task")
    