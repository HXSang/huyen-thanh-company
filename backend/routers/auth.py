from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import supabase, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies import get_current_user

router = APIRouter(tags=["Auth"])

def verify_password(plain_password: str, hashed_password: str):
    # Chuyển string sang bytes để bcrypt kiểm tra
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    response = supabase.table("nhan_vien").select("*").eq("email", form_data.username).execute()
    users = response.data
    
    if not users:
        raise HTTPException(status_code=400, detail="Sai email hoặc mật khẩu")
    
    user = users[0]

    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Sai email hoặc mật khẩu")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]},
        expires_delta=access_token_expires
    )

    supabase.table("nhan_vien").update(
        {"last_login_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", user["id"]).execute()

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"message": "Ngon lành! Token hợp lệ.", "user_info": current_user}