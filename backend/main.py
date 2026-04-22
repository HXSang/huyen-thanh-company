from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, san_pham, don_hang, khach_hang, utilities

app = FastAPI(title="Huyền Thanh Quote API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(san_pham.router)
app.include_router(don_hang.router)
app.include_router(khach_hang.router)
app.include_router(utilities.router)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Kiến trúc đã được refactor chuẩn mực!"}