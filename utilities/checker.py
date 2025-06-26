from fastapi import HTTPException, status, Depends
from .jwt_handler import get_current_user

class RoleChecker:
    async def check_admin(user: dict = Depends(get_current_user)):
        user = user.get("role")
        if user != "admin": 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Insufficient Priviledges")
        
    async def check_role(user: dict = Depends(get_current_user)):
        user = user.get("role")
        if user not in ("admin", "superuser"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Insufficient Privileges")

      