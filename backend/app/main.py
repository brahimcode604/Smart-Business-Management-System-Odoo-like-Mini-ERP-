from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base, SessionLocal
from app.models import models
from app.controllers.controllers import router
from app.services.services import create_user
from app.schemas.schemas import UserCreate
from app.core import security
import os

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Business Management ERP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Setup initial admin user
def init_db():
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        user_in = UserCreate(username="admin", password="password123", email="admin@erp.com", role=models.RoleEnum.admin)
        create_user(db, user_in)
    db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to Mini ERP API"}
