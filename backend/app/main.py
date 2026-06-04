import os
import jwt
import datetime
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import hashlib

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./qfai.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

JWT_SECRET = "qfai-super-secret-key-12345"
JWT_ALGORITHM = "HS256"

# Many-to-Many association table for participants
panorama_participants = Table(
    "panorama_participants",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("panorama_id", Integer, ForeignKey("panoramas.id", ondelete="CASCADE"), primary_key=True)
)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)

class PanoramaDB(Base):
    __tablename__ = "panoramas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    category = Column(String(50), nullable=False)
    date_time = Column(String(50), nullable=False)  # ISO format string
    spots = Column(Integer, default=0)              # 0 means unlimited
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="activo")    # activo, cancelado
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    organizer = relationship("UserDB", foreign_keys=[organizer_id])
    participants = relationship("UserDB", secondary=panorama_participants, backref="joined_panoramas")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Qfai API — Plataforma de Panoramas Locales", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(token: str, db: Session = Depends(get_db)) -> UserDB:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token no válido o expirado")

class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str

class PanoramaCreateSchema(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None
    category: str
    date_time: str
    spots: int = Field(default=0, ge=0)
    location: str
    latitude: float
    longitude: float

class PanoramaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    category: str
    date_time: str
    spots: int
    location: str
    latitude: float
    longitude: float
    status: str
    organizer_id: int
    organizer_name: str
    participants_count: int
    is_joined: Optional[bool] = False

@app.post("/api/auth/register", status_code=201)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.username == data.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    if db.query(UserDB).filter(UserDB.email == data.email).first():
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    new_user = UserDB(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(new_user.id, new_user.username)
    return {"token": token, "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}

@app.post("/api/auth/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not user or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    
    token = create_access_token(user.id, user.username)
    return {"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(token: str, db: Session = Depends(get_db)):
    return get_current_user(token, db)

@app.post("/api/panoramas", response_model=PanoramaResponse, status_code=201)
def create_panorama(data: PanoramaCreateSchema, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    try:
        dt = datetime.datetime.fromisoformat(data.date_time.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
        else:
            now = datetime.datetime.now()
        if dt < now:
            raise HTTPException(status_code=400, detail="La fecha del panorama debe ser futura")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
        
    if data.spots > 0 and data.spots < 2:
        raise HTTPException(status_code=400, detail="El cupo mínimo si se define debe ser 2")
        
    new_pan = PanoramaDB(
        title=data.title,
        description=data.description,
        category=data.category,
        date_time=data.date_time,
        spots=data.spots,
        location=data.location,
        latitude=data.latitude,
        longitude=data.longitude,
        organizer_id=user.id
    )
    db.add(new_pan)
    db.commit()
    db.refresh(new_pan)
    
    return PanoramaResponse(
        id=new_pan.id,
        title=new_pan.title,
        description=new_pan.description,
        category=new_pan.category,
        date_time=new_pan.date_time,
        spots=new_pan.spots,
        location=new_pan.location,
        latitude=new_pan.latitude,
        longitude=new_pan.longitude,
        status=new_pan.status,
        organizer_id=new_pan.organizer_id,
        organizer_name=user.username,
        participants_count=0,
        is_joined=False
    )

@app.get("/api/panoramas", response_model=List[PanoramaResponse])
def get_panoramas(
    category: Optional[str] = None,
    city: Optional[str] = None,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PanoramaDB).filter(PanoramaDB.status == "activo")
    if category and category.lower() != "todas":
        query = query.filter(PanoramaDB.category == category)
    if city:
        query = query.filter(PanoramaDB.location.like(f"%{city}%"))
    panoramas = query.all()
    
    current_user_id = None
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = payload.get("user_id")
        except Exception:
            pass
            
    res = []
    for p in panoramas:
        is_joined = False
        if current_user_id:
            is_joined = any(u.id == current_user_id for u in p.participants)
        res.append(PanoramaResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            category=p.category,
            date_time=p.date_time,
            spots=p.spots,
            location=p.location,
            latitude=p.latitude,
            longitude=p.longitude,
            status=p.status,
            organizer_id=p.organizer_id,
            organizer_name=p.organizer.username,
            participants_count=len(p.participants),
            is_joined=is_joined
        ))
    res.sort(key=lambda x: x.date_time)
    return res

@app.get("/api/panoramas/{id}", response_model=PanoramaResponse)
def get_panorama_detail(id: int, token: Optional[str] = None, db: Session = Depends(get_db)):
    p = db.query(PanoramaDB).filter(PanoramaDB.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panorama no encontrado")
    current_user_id = None
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = payload.get("user_id")
        except Exception:
            pass
    is_joined = False
    if current_user_id:
        is_joined = any(u.id == current_user_id for u in p.participants)
    return PanoramaResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        category=p.category,
        date_time=p.date_time,
        spots=p.spots,
        location=p.location,
        latitude=p.latitude,
        longitude=p.longitude,
        status=p.status,
        organizer_id=p.organizer_id,
        organizer_name=p.organizer.username,
        participants_count=len(p.participants),
        is_joined=is_joined
    )

@app.post("/api/panoramas/{id}/join")
def join_panorama(id: int, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    p = db.query(PanoramaDB).filter(PanoramaDB.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panorama no encontrado")
    if p.status == "cancelado":
        raise HTTPException(status_code=400, detail="No te puedes unir a un panorama cancelado")
    if p.organizer_id == user.id:
        raise HTTPException(status_code=400, detail="El organizador ya forma parte del panorama por defecto")
    if any(u.id == user.id for u in p.participants):
        return {"message": "Ya eres participante de este panorama"}
    if p.spots > 0 and len(p.participants) >= p.spots:
        raise HTTPException(status_code=400, detail="El panorama ya ha completado su cupo máximo")
    p.participants.append(user)
    db.commit()
    return {"message": "Te has unido al panorama con éxito"}

@app.post("/api/panoramas/{id}/leave")
def leave_panorama(id: int, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    p = db.query(PanoramaDB).filter(PanoramaDB.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panorama no encontrado")
    if not any(u.id == user.id for u in p.participants):
        raise HTTPException(status_code=400, detail="No participas en este panorama")
    p.participants.remove(user)
    db.commit()
    return {"message": "Has salido del panorama"}

@app.put("/api/panoramas/{id}", response_model=PanoramaResponse)
def edit_panorama(id: int, data: PanoramaCreateSchema, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    p = db.query(PanoramaDB).filter(PanoramaDB.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panorama no encontrado")
    if p.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este panorama")
    p.title = data.title
    p.description = data.description
    p.category = data.category
    p.date_time = data.date_time
    p.spots = data.spots
    p.location = data.location
    p.latitude = data.latitude
    p.longitude = data.longitude
    db.commit()
    db.refresh(p)
    return PanoramaResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        category=p.category,
        date_time=p.date_time,
        spots=p.spots,
        location=p.location,
        latitude=p.latitude,
        longitude=p.longitude,
        status=p.status,
        organizer_id=p.organizer_id,
        organizer_name=user.username,
        participants_count=len(p.participants),
        is_joined=False
    )

@app.delete("/api/panoramas/{id}")
def cancel_panorama(id: int, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    p = db.query(PanoramaDB).filter(PanoramaDB.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panorama no encontrado")
    if p.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para cancelar este panorama")
    p.status = "cancelado"
    db.commit()
    return {"message": "Panorama cancelado con éxito"}

@app.get("/api/users/profile")
def get_user_profile(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    organized = db.query(PanoramaDB).filter(PanoramaDB.organizer_id == user.id).all()
    joined_query = db.query(PanoramaDB).join(panorama_participants).filter(panorama_participants.c.user_id == user.id).all()
    def serialize_pan(p):
        return {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "date_time": p.date_time,
            "location": p.location,
            "status": p.status,
            "participants_count": len(p.participants)
        }
    return {
        "user": {"id": user.id, "username": user.username, "email": user.email},
        "organized": [serialize_pan(p) for p in organized],
        "joined": [serialize_pan(p) for p in joined_query]
    }