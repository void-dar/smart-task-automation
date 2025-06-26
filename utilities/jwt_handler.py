import jwt
from ..config import settings
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


JWT_SECRET = settings.JWT_SECRET
algorithm = settings.JWT_ALGORITM
ACCESS_TOKEN_EXPIRE=timedelta(seconds=900)
REFRESH_TOKEN_EXPIRE=timedelta(days=7)


async def create_email_token(payload):
    expiration_time = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    payload['exp'] = expiration_time
    try:
        token = jwt.encode(payload, JWT_SECRET, algorithm=algorithm)
        return token
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create email token")


async def create_access_token(payload):
    expiration_time = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    payload['exp'] = expiration_time
    try:
        token = jwt.encode(payload, JWT_SECRET, algorithm=algorithm)
        return f"Bearer {token}"
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create access token")

async def verify_token(token):
    try:
        user_data = jwt.decode(token, JWT_SECRET, algorithms=algorithm)
        return user_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token is invalid")
    
async def create_refresh_token(payload):
    expiration_time = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE
    payload['exp'] = expiration_time
    try:
        refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=algorithm)
        return refresh_token
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create refresh token")



security = HTTPBearer()
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = await verify_token(token)
        print (payload)
        return payload # or payload["sub"], etc.
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

async def verify_email_token(token: str) -> dict:
    try:
        # Decode and verify the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[algorithm]) 
        
        
        email = payload["email"]
        uid = payload["uid"]
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        if uid is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Here, you would mark the user's account as verified in your database
        # For example: db.users.update({'email': email}, {'$set': {'is_verified': True}})
        
        return {"email": email, "uid": uid}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    


async def verify_password_token(token: str) -> dict:
    try:
        # Decode and verify the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[algorithm]) 
        
        
        email = payload["email"]
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
       
        return {"email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")