from fastapi import APIRouter, status, Depends, HTTPException, Response, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select, and_
from ..schemas import CreateUser, UserOut, LogIn, ForgotPasswordRequest, OTPVerifyRequest, ResetPasswordRequest
from ..db.models import UserDB
from ..db.main import AsyncSession, get_db, redis_client
from fastapi.encoders import jsonable_encoder
from .auth import hash_password, verify_password
from datetime import datetime, timezone, timedelta
from ..utilities.jwt_handler import create_access_token, create_refresh_token, create_email_token, verify_email_token
from ..utilities.email import send_verification_email, serializer
import secrets
from ..utilities.utils import limiter



login_service = APIRouter()

@login_service.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_user(request: Request, background: BackgroundTasks, user: CreateUser, db: AsyncSession = Depends(get_db)):
    statement = select(UserDB).where(user.email == UserDB.email)
    result = await db.exec(statement)
    result = result.first()
    if result or None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    else:
        try:
            hashpassword = hash_password(user.password)


            new_user = UserDB(username=user.username, email=user.email, hashpassword=hashpassword, role=user.role)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            token = create_email_token({"email": user.email, "uid": UserDB.uid})

            url = f"{request.url}{token}"
            token = serializer.dumps(url)
            short_url = f"{request.url}{token}"
            
    
    # Create the email content
            content = f"Please verify your email by clicking the link: {short_url}"
            background.add_task(send_verification_email, user.email, body=content )
           
            
            return {"message": "User created successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create user: {str(e)}")
    
    
    
@login_service.post("/login", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def login_user(request: Request, response: Response, background: BackgroundTasks, user: LogIn, db: AsyncSession = Depends(get_db)):

     statement = select(UserDB).where(user.email == UserDB.email)
     result = await db.exec(statement)
     result = result.first()
     if not result:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
     checker = verify_password(user.password, result.hashpassword)
     if checker:
         try:
            
             result.last_seen = datetime.now(timezone.utc)
            
             await db.commit()
             result = {**result.model_dump()}
             user_data = {"uid": jsonable_encoder(result["uid"]),"username":result["username"], "role": result["role"]}
             access = await create_access_token(user_data)
             response.headers["Authorization"] = access
             refresh = await create_refresh_token(user_data)
             response.set_cookie(key="refresh",
                                 value=refresh,
                                 httponly=True,
                                 secure=True, 
                                 max_age=60*60*24*7)
             content = f'''Your account was logged into 
             {datetime.now(timezone.utc)}'''
             background.add_task(send_verification_email, user.email, body=content)
             return {"message": "User logged in successfully", "access token": access }
         except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login failed")
     else:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
     

@login_service.get("/verify-token/{token}")
@limiter.limit("5/minute")
async def verify_token(request: Request, token: str):
    original_url = serializer.loads(token)
    return RedirectResponse(url=original_url)


@login_service.get("/verify-details/{token}")
@limiter.limit("5/minute")
async def verify_email(request: Request, token: str, db: AsyncSession = Depends(get_db)):


    payload = await verify_email_token(token)
    email = payload.get("email")
    uid = payload.get("uid")
   
    try:
        statement = select(UserDB).where(and_(UserDB.uid == uid, UserDB.email == email))
        result = await db.exec(statement)
        result = result.first()
        if result is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Details not found")

        result.is_verified = True
        await db.commit()
        await db.refresh(result)
        return {"message":"Email Verified"}
    except: 
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='email verification failed')



@login_service.get("forgot_password")
@limiter.limit("5/minute")  
async def forgot(request: Request, background: BackgroundTasks, data: ForgotPasswordRequest):
    otp = str(secrets.randbelow(1000000)).zfill(6)  # 6-digit
    key = f"otp:{data.email}"
    
    if redis_client.get(key):
        raise HTTPException(status_code=400, detail="OTP already sent. Please wait.")

    redis_client.setex(key, timedelta(minutes=10), otp)  # TTL 10 min

    content = f"OTP for {data.email}: {otp}"
    background.add_task(send_verification_email, data.email, body=content )
    return {"message": "OTP sent to your email."}

@login_service.post("/verify-otp")
@limiter.limit("10/minute")
async def verify_otp(request: Request, data: OTPVerifyRequest):
    key = f"otp:{data.email}"
    stored_otp = await redis_client.get(key)

    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified"}

@login_service.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    key = f"otp:{data.email}"
    stored_otp = redis_client.get(key)

    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    # Simulate saving new password
    new_hash_password = hash_password(data.password)
    try:
        statement = select(UserDB).where(UserDB.email == data.email)
        result = await db.exec(statement)
        result = result.first()

        result.hashpassword = new_hash_password
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed")


    redis_client.delete(key)  # Delete OTP

    return {"message": "Password reset successful"}
