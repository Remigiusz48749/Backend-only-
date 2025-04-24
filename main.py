from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Boolean, DateTime, func, Column, Integer, String, Float, Sequence, select, update, delete, asc, desc
from pydantic import BaseModel, validator
from typing import List
from datetime import datetime
from passlib.context import CryptContext
from jose import JWTError, jwt


#for jwt
SECRET_KEY = "{YF73HBYzudd6al->$T^-*2!Lddig_"
ALGORITHM = "HS256"

# Konfiguracja bazy danych
DATABASE_URL = "postgresql+asyncpg://user:password@db/shopping_list"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

#Model ORM
class ShopItem(Base):
    __tablename__ = "items"
    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    category = Column(String, nullable=True)
    purchased = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

#crypting
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Users
class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, unique=True, index=True)
    hashed_password = Column(String)

# Tworzenie aplikacji FastAPI
app = FastAPI()

# Authoryzacja
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Tworzenie tabel w bazie danych
async def init_db():
    async with engine.begin() as conn:
        # Drop and recreate all tables
        await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

# Dependency do sesji bazy danych
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

#Pydantic
class ItemCreate(BaseModel):
    name: str
    quantity: int | None = None
    note: str | None = None
    category: str | None = None
    purchased: bool = False

class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: int | None = None
    note: str | None = None
    category: str | None = None
    purchased: bool
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        orm_mode = True

    @validator('created_at', 'updated_at', pre=True)
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

#For Registry
class RegisterRequest(BaseModel):
    username: str
    password: str
    repeated_password: str

#For Login
class LoginRequest(BaseModel):
    username: str
    password: str

#for Log and Registry
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def hash_password(password: str):
    return pwd_context.hash(password)

#JWT
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception

    return user


# Endpoint: Pobierz wszystkie kawy
@app.get("/items/", response_model=List[ItemResponse])
async def get_items(
    current_user: User = Depends(get_current_user),
    name: str | None = Query(None),
    category: str | None = Query(None),
    purchased: bool | None = Query(None),
    sort_by: str | None = Query(None, regex="^(createdAt|updatedAt)$"),
    sort_order: str | None = Query("asc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    query = select(ShopItem)

    if name:
        query = query.where(ShopItem.name.ilike(f"%{name}%"))
    if category:
        query = query.where(ShopItem.category == category)
    if purchased is not None:
        query = query.where(ShopItem.purchased == purchased)
    
    if sort_by:
        sort_column = ShopItem.created_at if sort_by == "createdAt" else ShopItem.updated_at
        query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    result = await db.execute(query)
    return result.scalars().all()

# Endpoint: Dodaj nową kawę
@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(item: ItemCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_item = ShopItem(**item.dict())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

# Endpoint: Dodaj wiele elementów na raz
@app.post("/items/bulk", response_model=List[ItemResponse], status_code=status.HTTP_201_CREATED)
async def add_multiple_items(items: List[ItemCreate], current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_items = [ShopItem(**item.dict()) for item in items]
    db.add_all(new_items)
    await db.commit()
    for item in new_items:
        await db.refresh(item)
    return new_items

# Endpoint: Pobierz kawę po ID
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_by_id(item_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShopItem).where(ShopItem.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item

# Endpoint: Zaktualizuj kawę
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_data: ItemCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShopItem).where(ShopItem.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

    for key, value in item_data.dict().items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

# Endpoint: Usuń kawę
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShopItem).where(ShopItem.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

    await db.delete(item)
    await db.commit()
    return

# Endpoint: Usuń all
@app.delete("/items/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_items(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ShopItem))
    await db.commit()
    return

# Endpoint: registry
@app.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not data.username or not data.password or not data.repeated_password:
        raise HTTPException(status_code=400, detail="All fields are required.")

    if data.password != data.repeated_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    existing = await get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")

    new_user = User(
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    db.add(new_user)
    await db.commit()

    return {"message": "User registered successfully."}

# Endpoint: login
@app.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, data.username)

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}
