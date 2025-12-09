from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, and_
from .models import Base, User, Pet, Note
from config import DATABASE_URL
import asyncio

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# User helpers
async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession):
    q = select(User).where(User.telegram_id == telegram_id)
    res = await session.execute(q)
    return res.scalar_one_or_none()

async def create_user_if_not_exists(telegram_id: int, session: AsyncSession):
    user = await get_user_by_telegram_id(telegram_id, session)
    if user:
        return user, False
    user = User(telegram_id=telegram_id)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True

# Pet helpers
async def create_pet(user_id: int, breed: str, name: str, age: str, extra_info: str | None, session: AsyncSession):
    # check duplicate name for user
    q = select(Pet).where(and_(Pet.user_id == user_id, Pet.name == name))
    res = await session.execute(q)
    if res.scalar_one_or_none():
        raise ValueError("Duplicate pet name for this user.")
    pet = Pet(user_id=user_id, breed=breed, name=name, age=age, extra_info=extra_info)
    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return pet

async def get_pets_by_user(user_id: int, session: AsyncSession):
    q = select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at.asc())
    res = await session.execute(q)
    return res.scalars().all()

async def get_pet_by_name(user_id: int, pet_name: str, session: AsyncSession):
    q = select(Pet).where(and_(Pet.user_id == user_id, Pet.name == pet_name))
    res = await session.execute(q)
    return res.scalar_one_or_none()

async def update_pet(pet: Pet, session: AsyncSession, **kwargs):
    for k, v in kwargs.items():
        setattr(pet, k, v)
    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return pet

# Note helpers
async def create_note(pet_id: int, title: str, period: str, extra_info: str | None, session: AsyncSession):
    note = Note(pet_id=pet_id, title=title, period=period, extra_info=extra_info)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note

async def get_notes_by_pet(pet_id: int, session: AsyncSession):
    q = select(Note).where(Note.pet_id == pet_id).order_by(Note.created_at.asc())
    res = await session.execute(q)
    return res.scalars().all()

async def delete_note_by_id(note_id: int, session: AsyncSession):
    q = select(Note).where(Note.id == note_id)
    res = await session.execute(q)
    note = res.scalar_one_or_none()
    if note is None:
        return False
    await session.delete(note)
    await session.commit()
    return True

async def get_note_by_id(note_id: int, session: AsyncSession):
    q = select(Note).where(Note.id == note_id)
    res = await session.execute(q)
    return res.scalar_one_or_none()
