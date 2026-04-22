from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Kiểm tra token, giải mã lấy ID và Role của nhân viên"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nhan_vien_id: str = payload.get("sub")
        role: str = payload.get("role")
        if nhan_vien_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"nhan_vien_id": nhan_vien_id, "role": role}

def require_role(*roles: str):
    """Decorator chặn quyền. VD: Depends(require_role('admin'))"""
    async def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Không có quyền thực hiện thao tác này")
        return user
    return checker